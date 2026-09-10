import os
from argparse import ArgumentParser

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from layers.raw_layer import RawLayer
from layers.wiki_layer import WikiLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from utils.awrap_tool_call import AwrapToolCall
from utils.run_agent import run_deepagents
from pathlib import Path

load_dotenv()


_SYSTEM_PROMPT = """
You are a Wiki Maintainer Agent for an LLM skill evolution system.
Your job is to maintain a structured knowledge base (wiki) directly on the local filesystem that documents patterns observed during agent execution -- both successes and failures. You must perform DEEP ANALYSIS of execution logs to identify root causes, not just surface-level symptoms.

## Wiki Structure

**CRITICAL**: FULL WIKI DIRECTORY IS LOCATED AT `{wiki_dir}`. YOU MUST ALWAYS PERFORM ALL OPERATIONS WITHIN IT.
**CRITICAL**: DON'T CHANGE ANY README.MD FILES WHICH ARE THE DESCRIPTIONS OF THE WIKI STUFFS.
**CRITICAL**: AVOID TOUCHING (READ OR WRITE) README.md FILES. THE README.MD FILES ARE PURELY EXPLANATORY ARTIFACTS OF NO VALUE. **DISREGARD THEM ENTIRELY**.
**CRITICAL**: AVOID TOUCHING (READ OR WRITE) `.git/`
**CRITICAL**: AVOID EDITING, WRITING, DELETING `skill-impact.md`

This layer compiles raw **task execution traces** into structured, compounding knowledge. 
*Crucial Rule:* This directory is **PERMANENT and NEVER rolls back**. Even if a skill proposal is rejected, the diagnostic patterns and impact logs generated during that iteration persist here to guide future attempts.

The wiki is organized on disk as:
- `index.md` -- Concise catalog of known patterns (one line per pattern)
- `log.md` -- Chronological evolution log (iterations, scores, accept/reject)
- `skill-impact.md` -- Record of which skills were tried and their outcomes
- `patterns/` -- One page per pattern with detailed evidence and analysis (e.g., `patterns/pattern-name.md`)

## Your Input

1. Execution **traces** from the latest iteration -- including full agent execution logs showing what actions the agent took, what commands it ran, and what environment feedback it observed:

{traces}

2. The current wiki context (index, log, pattern pages) located on the local filesystem under `{wiki_dir}/`, accessible via your built-in filesystem tools.

## Available Filesystem Tools

You have direct access to the local filesystem through built-in tools:
- `ls(path)`: List files in a directory with metadata (size, modified time).
- `read_file(path, offset, limit)`: Read file contents with line numbers, supports offset/limit for large files.
- `write_file(path, content)`: Create a new file, or overwrite an existing one.
- `edit_file(path, old_string, new_string, replace_all)`: Perform exact string replacements in files.
- `glob(pattern)`: Find files matching patterns (e.g., `patterns/*.md`).
- `grep(pattern, path)`: Search file contents with regex or keyword patterns.

## Execution & Maintenance Workflow

Follow this step-by-step workflow during each evolution cycle:

1. **Analyze Execution Traces**:
   - Deeply inspect the execution traces provided in **traces**.
   - Perform root-cause analysis (see Deep Trace Analysis guidelines below).

2. **Inspect Existing Wiki State**:
   - Use `glob` or `ls` (e.g., `patterns/`) and `read_file("index.md")` within `{wiki_dir}` to understand current state.
   - Use `grep` or `read_file` on related pattern files to prevent duplicates.

3. **Create or Update Patterns**:
   - **For New Patterns**: Use `write_file("patterns/<pattern-name>.md", content)` to create the pattern document following the documentation rules.
   - **For Existing Patterns**: Use `edit_file` (or `write_file`) to enrich existing patterns with new evidence, updated fixes, or refined root cause analysis.

4. **Update `index.md` (MANDATORY)**:
   - You MUST ensure `index.md` reflects all current patterns, including any newly added or updated ones.
   - Read `index.md` first, update the catalog, and write the complete, updated index back using `write_file`.

5. **Append to `log.md` (MANDATORY)**:
   - You MUST record a brief chronological summary of this iteration's findings, decisions, and file changes into `log.md` using `edit_file` or `write_file`.

6. **Final Response**:
   - After completing all filesystem operations, output a concise summary of the iteration findings, root cause analysis, and a list of wiki files created or modified.

## Analysis Guidelines

### Deep Trace Analysis (CRITICAL)

When execution logs are provided, you MUST:
1. Read the agent’s actual actions -- what commands did it issue?
2. Compare successful vs failed tasks -- what did successful tasks do differently?
3. Identify ACTION PATTERNS and strategies, not just error messages.
4. Check whether the agent followed any active skills, and whether the skill guidance was helpful or not.

### Pattern Documentation Rules

1. Each pattern page should document:
   - What the pattern is (description)
   - Root cause analysis (WHY it happens, not just WHAT happens)
   - Exact command sequences from traces (what the agent did wrong / right)
   - Known solutions or workarounds (concrete action patterns with exact syntax)
2. Capture BOTH success and failure patterns:
   - **Failure patterns**: Document what went wrong and how to avoid it.
   - **Success patterns**: Document strategies that consistently lead to task completion.
3. Do NOT create duplicate patterns -- update existing ones with new evidence.
4. Be concise. Pattern pages should be 10-30 lines, not essays.
5. Only create patterns for meaningful, generalizable observations.

### Index Description Quality (CRITICAL)

The `index.md` entries are the MOST IMPORTANT part of the wiki because they determine whether inference agents will read the full pattern pages.
Each index entry MUST follow this format:
- `[pattern-name](patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.`

The description must be specific enough that an agent can judge relevance without reading the full page. Include the problem, root cause, AND solution.
"""


class WikiMaintainer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _wiki_layer: WikiLayer
    _raw_layer: RawLayer

    def __init__(self):
        self._model = init_chat_model(
            model=os.environ["WIKI_MANTANCER_MODEL"],
            model_provider="google_genai",
            temperature=float(os.environ["TEMPERATURE"]),
            vertexai=os.environ["GOOGLE_GENAI_USE_VERTEXAI"].lower() == "true",
            enterprise=os.environ["GOOGLE_GENAI_USE_ENTERPRISE"].lower() == "true",
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ["WIKI_MANTANCER_MODEL_LOCATION"],
            thinking_config={
                "thinking_level": os.environ["THINKING_LEVEL"],
                "include_thoughts": os.environ["INCLUDE_THOUGHTS"].lower() == "true",
            },
        )
        self._raw_layer = RawLayer()

    def _create_block_forbidden_files(self, root_dir):
        def _block_forbidden_files(request, handler):
            tool_name = request.tool_call.get("name", "")
            args = request.tool_call.get("args", {})

            raw_path = args.get("file_path") or args.get("path") or ""
            if not str(Path(raw_path).resolve()).startswith(
                str(Path(root_dir).resolve())
            ):
                logger.warning(
                    f"Block forbidden action on non-wiki directory: tool={tool_name}, path='{raw_path}', **ONLY ALLOWED** in '{root_dir}'"
                )
                return ToolMessage(
                    content=f"Access to the non-wiki directory is strictly forbidden. **ONLY ALLOWED** in '{root_dir}'",
                    name=tool_name,
                    tool_call_id=request.tool_call.get("id", "avoid"),
                )

            pattern = args.get("pattern") or ""
            file_name = os.path.basename(raw_path.rstrip("/\\"))
            path_parts = Path(raw_path).parts

            is_git_access = (
                ".git" in path_parts
                or raw_path.strip("/\\") == ".git"
                or ".git" in pattern.split("/")
                or pattern.startswith(".git")
            )
            if is_git_access:
                logger.warning(
                    f"Block forbidden action on .git directory: tool={tool_name}, path='{raw_path}', pattern='{pattern}'"
                )
                return ToolMessage(
                    content="Access to the '.git' directory and its contents is strictly forbidden.",
                    name=tool_name,
                    tool_call_id=request.tool_call.get("id", "avoid"),
                )

            if (
                tool_name in ("write_file", "edit_file", "delete")
                and file_name == "skill-impact.md"
            ):
                logger.warning(f"Block forbidden file {tool_name} on skill-impact.md")
                return ToolMessage(
                    content="The 'skill-impact.md' is a protected system log and must not be written, modified, or deleted.",
                    name=tool_name,
                    tool_call_id=request.tool_call.get("id", "avoid"),
                )

            _full_blocked_files = [
                ".gitignore",
                ".gitattributes",
                ".gitmodules",
                ".DS_Store",
                "readme.md",
                "README.md",
            ]
            if file_name.lower() in _full_blocked_files:
                logger.warning(
                    f"Block forbidden file {tool_name} of {_full_blocked_files}"
                )
                return ToolMessage(
                    content=f"The {file_name} is protected and must NOT be read, written, or modified. Full list of forbidden files: {_full_blocked_files}",
                    name=tool_name,
                    tool_call_id=request.tool_call.get("id", "avoid"),
                )

            return handler(request)

        return _block_forbidden_files

    async def __call__(self, **kwargs):
        traces_dir = kwargs["traces_dir"]
        assert os.path.exists(traces_dir)
        traces_abs_path = os.path.abspath(traces_dir)

        wiki_dir = kwargs["wiki_dir"]
        assert os.path.exists(wiki_dir)
        wiki_abs_path = os.path.abspath(wiki_dir)
        stream_mode = kwargs.get("stream_mode") == True

        traces_dict = self._raw_layer.read_traces(traces_abs_path)
        traces_str = str(traces_dict)
        system_prompt = _SYSTEM_PROMPT.format(wiki_dir=wiki_abs_path, traces=traces_str)
        logger.debug(f"system prompt:\n\n{system_prompt[:250]}...\n\n")
        backend = FilesystemBackend(root_dir=wiki_abs_path, virtual_mode=False)
        self._agent = create_deep_agent(
            model=self._model,
            backend=backend,
            middleware=[
                AwrapToolCall(self._create_block_forbidden_files(wiki_abs_path))
            ],
            system_prompt=system_prompt,
        )
        logger.info(
            f"Run WikiMaintainer, at {wiki_abs_path}, for traces:\n\n{traces_str[:100]}...\n\n"
        )

        messages = [{"role": "user", "content": "maintain the wiki please"}]
        await run_deepagents(self._agent, messages, stream_mode)
        logger.success("WikiMaintainer done")


async def main(args):
    wiki_maintainer = WikiMaintainer()
    await wiki_maintainer(
        traces_dir=args.traces_dir,
        wiki_dir=args.wiki_dir,
        stream_mode=args.stream_mode,
    )


if __name__ == "__main__":

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--traces_dir",
        type=str,
        required=True,
        help="Inference traces directory",
    )
    parser.add_argument(
        "--wiki_dir",
        type=str,
        required=True,
        help="Wiki directory (current state)",
    )
    parser.add_argument(
        "--stream_mode",
        action="store_true",
        help="Set for stream mode",
    )
    args = parser.parse_args()

    # python wiki_maintainer.py --traces_dir ../output/38a619f7-7614-4473-bc53-a5a3f46c2b81/1234455 --wiki_dir ../workspace/wiki --stream_mode
    import asyncio

    asyncio.run(main(args))
