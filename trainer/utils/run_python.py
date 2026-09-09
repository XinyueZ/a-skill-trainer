import io
import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, Optional

import docker
from langchain.tools import tool


def create_run_python(session_id: str, output_path: str = "./sandbox_output") -> tuple:
    """
    Create the tool that run python script.

    Args:
        session_id: The task session ID, used to create a unique container name.
        output_path: The path to store the output of the script.

    Return:
        tuple: (The run_python tool, A program python file path, the path to the Python script to execute. (main.py))


    """
    output_dir_host = Path(output_path).resolve() / str(session_id)
    output_dir_host.mkdir(parents=True, exist_ok=True)
    program_file_path = str(output_dir_host / "main.py")

    @tool
    def run_python(
        program_file_path: str, extra_env_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """Run a Python script safely inside an isolated Docker sandbox container.

        Use this tool after writing a script with `write_file` to execute it and get stdout/stderr results.

        Args:
            program_file_path: The path to the Python script to execute.
            extra_env_vars: Optional environment variables to inject into the container.

        Returns:
            A string containing the execution stdout/stderr and exit status.
        """
        target = Path(program_file_path).resolve()
        code_dir_host = target.parent

        if not target.exists() or not target.is_file():
            return f"ExecutionError: Python file not found at '{target}'"

        if not Path("/var/run/docker.sock").exists():
            return "DockerUnavailable: /var/run/docker.sock not found. Please ensure Docker daemon is running."

        filename = target.name
        ctr_code = "/work/code"
        ctr_output = "/work/output"
        ctr_target = f"{ctr_code}/{filename}"

        run_script = f'set -e; cd {ctr_output} && python -B "{ctr_target}"'
        command = ["sh", "-lc", run_script]

        container = None
        try:
            client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
            container = client.containers.run(
                image="python:3.13-slim",
                command=["sh", "-lc", "sleep 3600"],
                detach=True,
                remove=False,
                network_mode="bridge",
                read_only=False,
                working_dir="/work",
                tmpfs={"/tmp": "rw,noexec,nosuid,nodev,size=256m"},
                mem_limit="1g",
                nano_cpus=int(2.0 * 1_000_000_000),
                pids_limit=50,
                security_opt=["no-new-privileges:true"],
                environment={
                    **(extra_env_vars or {}),
                    "HOME": "/work",
                    "PIP_CACHE_DIR": "/work/pip-cache",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONUSERBASE": "/work/.local",
                    "PATH": "/usr/local/bin:/usr/bin:/bin:/work/.local/bin",
                },
            )

            rc, _ = container.exec_run(
                cmd=[
                    "sh",
                    "-c",
                    f"mkdir -p {ctr_code} {ctr_output} /work/pip-cache && chown -R 1000:1000 /work",
                ],
                user="0",
            )
            if int(rc) != 0:
                return (
                    "ExecutionError: Failed to initialize directories inside container."
                )

            tar_buf = io.BytesIO()
            with tarfile.open(fileobj=tar_buf, mode="w") as tf:
                tf.add(str(code_dir_host), arcname="code")
            tar_buf.seek(0)
            container.put_archive("/work", tar_buf.read())

            rc, out = container.exec_run(
                cmd=command,
                user="1000:1000",
                demux=False,
            )
            logs = (out or b"").decode("utf-8", errors="replace")

            try:
                stream, _ = container.get_archive(ctr_output)
                out_tar = io.BytesIO(b"".join(stream))
                out_tar.seek(0)
                with tempfile.TemporaryDirectory() as td:
                    with tarfile.open(fileobj=out_tar, mode="r:*") as tf:
                        tf.extractall(path=td)
                    extracted = Path(td) / "output"
                    if extracted.exists():
                        shutil.copytree(
                            str(extracted), str(output_dir_host), dirs_exist_ok=True
                        )
            except Exception as e:
                logs += f"\n[Warning: Failed to sync output files back to host: {e}]"

            if int(rc) != 0:
                return f"❌ Execution Failed (Exit Code {rc}):\n{logs}"

            return f"✅ Execution Succeeded:\n{logs}"

        except Exception as e:
            return f"ExecutionError: {e}"
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    return run_python, program_file_path
