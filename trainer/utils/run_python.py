import os

from pathlib import Path
from typing import Dict, Optional

import docker


def create_run_python(output_path: Path):
    """
    Create the tool that run python script.

    Args:
        output_path: The path to store the output of the script.

    Return:
        The run_python tool
    """

    output_path.mkdir(parents=True, exist_ok=True)
    program_file_path = os.path.join(str(output_path), "main.py")
    with open(program_file_path, "w", encoding="utf-8") as f:
        f.write("")

    def run_python(
        program_code: str, extra_env_vars: Optional[Dict[str, str]] = None
    ) -> str:
        """Run a Python script safely inside an isolated Docker sandbox container.

        Args:
            program_code: full preogram code to execute.
            extra_env_vars: Optional environment variables to inject into the container.

        Returns:
            A string containing the execution stdout/stderr and exit status.
        """
        with open(program_file_path, "w", encoding="utf-8") as f:
            f.write(program_code)

        target = Path(program_file_path).resolve()
        output_dir_host = output_path

        if not target.exists() or not target.is_file():
            return f"ExecutionError: Python file not found at '{target}'"

        if not Path("/var/run/docker.sock").exists():
            return "DockerUnavailable: /var/run/docker.sock not found. Please ensure Docker daemon is running."

        filename = target.name
        command = ["sh", "-lc", f'cd /work && python -B "{filename}"']

        container = None
        try:
            client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
            volumes_config = {
                str(output_dir_host.resolve()): {"bind": "/work", "mode": "rw"}
            }
            container = client.containers.run(
                image="python:3.13-slim",
                command=["sh", "-lc", "sleep 3600"],
                detach=True,
                remove=False,
                network_mode="bridge",
                read_only=False,
                working_dir="/work",
                volumes=volumes_config,
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

            rc, out = container.exec_run(
                cmd=command,
                user="1000:1000",
                demux=False,
            )
            logs = (out or b"").decode("utf-8", errors="replace")
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

    return run_python
