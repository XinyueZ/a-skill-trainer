import os
from argparse import ArgumentParser
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from layers.raw_layer import RawLayer
from layers.skills_layer import SkillsLayer
from layers.wiki_layer import WikiLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from utils.awrap_tool_call import AwrapToolCall
from utils.run_agent import run_deepagents
from langchain.tools import tool

load_dotenv()
_SYSTEM_PROMPT = """
You are a Skill Proposer Agent for an LLM agent that solves task:

{task_desc}

Your job is to explore the wiki knowledge base and **task execution traces**, diagnose root causes of failures, and propose a skill change (create or patch).

**CRITICAL**: YOUR WORKSPACE DIRECTORY IS LOCATED AT `{workspace_dir}`. 
**CRITICAL**: EVERYTHING AT `{workspace_dir}` IS **READ-ONLY**.
**CRITICAL**: DON'T CHANGE ANY README.MD FILES WHICH ARE THE DESCRIPTIONS OF THE WORKSPACE STUFFS.
**CRITICAL**: AVOID TOUCHING (READ OR WRITE) README.md FILES. THE README.MD FILES ARE PURELY EXPLANATORY ARTIFACTS OF NO VALUE. **DISREGARD THEM ENTIRELY**.
**CRITICAL**: AVOID TOUCHING (READ OR WRITE) `.git/`, `.gitignore, `.DS_Store`
The workspace is organized into distinct layers to separate raw experience, compiled knowledge, and executable code. You must understand the role of each directory to operate effectively:

### 1. `wiki/` (Persistent Knowledge Layer)
This layer compiles raw **task execution traces** into structured, compounding knowledge. 
*Crucial Rule:* This directory is **PERMANENT and NEVER rolls back**. Even if a skill proposal is rejected, the diagnostic patterns and impact logs generated during that iteration persist here to guide future attempts.

*   `wiki/index.md`: A global, content-oriented catalog indexing all known behavior patterns. Each entry links to its pattern page with a one-sentence summary of the problem, root cause, and fix.
*   `wiki/log.md` (or `logs.md`): A chronological, append-only history of the wiki's evolution. It summarizes the findings, errors, and maintainer actions for each iteration.
*   `wiki/skill-impact.md`: An objective audit trail maintained programmatically by the outer-loop harness. It records every past proposal, its target skill, its complete Git Diff, validation scores, and the final decision (Accepted or Rejected). **You MUST read this first and NEVER propose a change that was previously rejected.**
*   `wiki/patterns/`: A directory containing individual Markdown files (`*.md`) for specific failure modes or success strategies. Each file details root-cause analysis, exact trace evidence, and concrete workarounds.

### 2. `skills/` (Active Skills Layer)
This layer contains the active set of evolved procedural skills that are directly injected into the Inference Agent's system prompt.
*Crucial Rule:* This directory is **REVERSIBLE**. If your proposal degrades validation performance, the entire modifications under this directory will be **simultaneously rolled back** to the previous stable state.

*   Each skill exists as a standalone directory: `skills/<skill_name>/`.
*   `skills/<skill_name>/SKILL.md`: The executable instruction file. It contains YAML frontmatter metadata (name, description), "When to Apply" rules, and actionable guidelines.
*   `skills/<skill_name>/PURPOSE.md`: The design intent file. It documents the skill's origin, the list of motivating Wiki patterns it addresses, and its evolution history. **The status of SKILL.md and PURPOSE.md is strictly synchronized; they are created, updated, or rolled back together.**

## Tools Available
 
You have direct access to the local filesystem through built-in tools:
- `ls(path)`: List files in a directory with metadata (size, modified time).
- `read_file(path, offset, limit)`: Read file contents with line numbers, supports offset/limit for large files.
- `glob(pattern)`: Find files matching patterns (e.g., `patterns/*.md`).
- `grep(pattern, path)`: Search file contents with regex or keyword patterns.

** Special tool after finalization of proposal**:
- `finish(proposal)` -- Submit your final skill proposal as a JSON object.

## Workflow

1. Start by reading `wiki/index.md` to understand what patterns exist
2. Read `wiki/skill-impact.md` to see what was tried before (includes full content of rejected proposals -- DO NOT repeat rejected approaches)
3. Read specific pattern pages that seem relevant to the current failures
4. Read **task execution traces** for failed tasks via `traces` to understand root causes
5. Decide: create (new skill) or patch (edit existing skill), or no_action
6. If proposing a change, call `finish` with the full proposal

## `finish(proposal)` Proposal Format

For creating a new skill:
- "action": "create"
- "name": skill **directory name** (**CRITICAL**: kebab-case, ie: user-profile-data, run-android-app)
- "skill_md": full SKILL.md content with YAML frontmatter + When to Apply + When NOT to Apply + Instructions
- "purpose_md": full PURPOSE.md content with Origin + Patterns Addressed + Evolution
History

For patching an existing skill:
- "action": "patch"
- "name": existing skill **directory name**  (**CRITICAL**: kebab-case, id: user-profile-data, run-android-app....)
- "skill_edits": list of patch operations for SKILL.md (empty if no changes needed):
  - {{"op": "append", "content": "text to add at end"}}
  - {{"op": "replace", "target": "exact text to find", "content": "replacement"}}
  - {{"op": "insert_after", "target": "exact text to find", "content": "text to insert after"}}
- "purpose_edits": list of patch operations for PURPOSE.md (empty if no changes needed):
  - {{"op": "append", "content": "text to add at end"}}
  - {{"op": "replace", "target": "exact text to find", "content": "replacement"}}
  - {{"op": "insert_after", "target": "exact text to find", "content": "text to insert after"}}

**Rules**:
1. Each "replace" target should be a short, specific section. If you need to change most of either file, use "action": "create" instead. If no action is needed, call finish with: {{"action": "no_action"}}

## Rules
1. Read the wiki FIRST -- don’t propose something that was already tried and rejected. skill-impact.md contains full content of rejected proposals.
2. Focus on action patterns and concrete strategies.
3. Keep skills concise and actionable.
4. You MUST read the task execution traces before proposing a skill change. Target your exploration based on the trace summary.
5. Prefer patching existing skills over creating new ones when the existing skill is partially correct.
"""

import re
from typing import List, Literal, Optional

from langchain.tools import tool
from pydantic import BaseModel, Field, field_validator, model_validator


class PatchOperation(BaseModel):
    file: Literal["SKILL.md", "PURPOSE.md"] = Field(
        default="SKILL.md", description="Target file for the patch."
    )
    op: Literal["append", "replace", "insert_after"] = Field(
        ..., description="Type of patch operation."
    )
    target: Optional[str] = Field(
        default=None,
        description="Required anchor text for 'replace' and 'insert_after'.",
    )
    content: str = Field(..., description="The content to apply.")

    @model_validator(mode="after")
    def validate_and_heal_target(self) -> "PatchOperation":
        if self.op in ("replace", "insert_after") and not self.target:
            raise ValueError(f"Operation '{self.op}' requires a 'target' substring.")

        if self.op == "append" and self.target is not None:
            self.target = None
        return self


class CreateSkillProposal(BaseModel):
    action: Literal["create"]
    name: str = Field(..., description="Snake_case directory name.")
    skill_md: str = Field(..., description="Full content of SKILL.md.")
    purpose_md: str = Field(..., description="Full content of PURPOSE.md.")

    @field_validator("name")
    @classmethod
    def sanitize_skill_name(cls, v: str) -> str:
        cleaned = v.replace(".md", "").split("/")[-1]
        cleaned = re.sub(r"[^a-zA-Z0-9_\-]+", "-", cleaned).lower().strip("-")
        if not cleaned:
            raise ValueError(f"Invalid skill name format: {v}")
        return cleaned


class PatchSkillProposal(BaseModel):
    action: Literal["patch"]
    name: str = Field(..., description="Skill directory to patch.")
    edits: List[PatchOperation] = Field(..., description="List of patch edits.")

    @field_validator("name")
    @classmethod
    def sanitize_existing_name(cls, v: str) -> str:
        return v.replace(".md", "").split("/")[-1].strip().lower()


class NoActionProposal(BaseModel):
    action: Literal["no_action"] = "no_action"
    reason: str = Field(
        default="Automatically falls back to no_action due to critical format validation failure.",
        description="Reason for taking no action.",
    )


def _create_finish_tool(output_dir: Path, session_id: str, task_id: str):
    output_file_path = os.path.join(
        str(output_dir),
        session_id,
        task_id,
        "proposal.json",
    )

    @tool
    def finish(
        proposal_dict: dict,
    ) -> CreateSkillProposal | PatchSkillProposal | NoActionProposal:
        """
        Submit your final skill proposal as a JSON object. Called after finalization of proposal.

        Args:
        - proposal_dict: The proposal to submit.

        Returns:
        - A JSON object representing the final proposal.
        """

        p: CreateSkillProposal | PatchSkillProposal | NoActionProposal
        # from rich.pretty import pprint as pp
        # pp(proposal_dict)

        if not isinstance(proposal_dict, dict):
            logger.error(f"Input to finish() is not a dict! Got: {type(proposal_dict)}")
            p = NoActionProposal(
                reason="Critical failure: input payload is not a JSON object."
            )
            Path(output_file_path).write_text(
                p.model_dump_json(indent=2), encoding="utf-8"
            )
            return p

        payload = dict(proposal_dict)
        action_raw = str(payload.get("action", "")).strip().lower()

        if action_raw in ("create", "created", "new", "make"):
            payload["action"] = "create"
        elif action_raw in ("patch", "patched", "update", "updated", "edit", "edits"):
            payload["action"] = "patch"
        elif action_raw in ("no_action", "noaction", "none", "no-action", "nothing"):
            payload["action"] = "no_action"
        else:
            logger.warning(
                f"Unidentified action: '{action_raw}'. Overwriting with 'no_action'."
            )
            payload["action"] = "no_action"

        action = payload["action"]
        if action == "create":
            if "purpose_md" not in payload or not str(payload["purpose_md"]).strip():
                logger.warning(
                    "Create proposal is missing 'purpose_md'. Self-healing with default template."
                )
                payload["purpose_md"] = (
                    f"# PURPOSE\n\n- **Origin**: Created for skill '{payload.get('name', 'unnamed')}' "
                    "to address recurring behavior patterns."
                )

            if "skill_md" not in payload:
                payload["skill_md"] = (
                    "# SKILL INSTRUCTIONS\n\nNo instructions provided."
                )
        elif action == "patch":
            raw_edits = []
            has_separated_edits = "skill_edits" in payload or "purpose_edits" in payload
            if has_separated_edits:
                skill_edits = payload.get("skill_edits") or []
                if isinstance(skill_edits, list):
                    for e in skill_edits:
                        if isinstance(e, dict):
                            item = dict(e)
                            item.setdefault("file", "SKILL.md")
                            raw_edits.append(item)

                purpose_edits = payload.get("purpose_edits") or []
                if isinstance(purpose_edits, list):
                    for e in purpose_edits:
                        if isinstance(e, dict):
                            item = dict(e)
                            item.setdefault("file", "PURPOSE.md")
                            raw_edits.append(item)

            else:
                legacy_edits = payload.get("edits") or payload.get("edit") or []
                if isinstance(legacy_edits, list):
                    for e in legacy_edits:
                        if isinstance(e, dict):
                            item = dict(e)
                            item.setdefault("file", "SKILL.md")
                            raw_edits.append(item)

                elif "op" in payload and "content" in payload:
                    logger.warning(
                        "Single edit found flat on root. Packaging into edits list."
                    )
                    raw_edits.append(
                        {
                            "file": payload.get("file", "SKILL.md"),
                            "op": payload["op"],
                            "target": payload.get("target"),
                            "content": payload["content"],
                        }
                    )

            sanitized_edits = []
            for index, edit in enumerate(raw_edits):
                edit_copy = dict(edit)
                op_raw = str(edit_copy.get("op", "")).strip().lower()
                if op_raw in ("append", "add", "push"):
                    edit_copy["op"] = "append"
                elif op_raw in ("replace", "overwrite", "update", "change"):
                    edit_copy["op"] = "replace"
                elif op_raw in ("insert_after", "insert", "after"):
                    edit_copy["op"] = "insert_after"
                else:
                    logger.warning(
                        f"Discarding invalid edit operation at index {index}: '{op_raw}'"
                    )
                    continue
                sanitized_edits.append(edit_copy)

            if not sanitized_edits:
                logger.warning(
                    "Patch action specified but no valid edits found (both skill_edits and purpose_edits are empty). "
                    "Falling back to 'no_action'."
                )
                p = NoActionProposal(
                    action="no_action",
                    reason="Patch action contained no valid edits for SKILL.md or PURPOSE.md.",
                )
                Path(output_file_path).write_text(
                    p.model_dump_json(indent=2), encoding="utf-8"
                )
                return p

            payload["edits"] = sanitized_edits

        try:
            if action == "create":
                p = CreateSkillProposal(**payload)
            elif action == "patch":
                p = PatchSkillProposal(**payload)
            else:
                p = NoActionProposal(
                    action="no_action",
                    reason=payload.get(
                        "reason", "Inference ended with explicit no_action."
                    ),
                )
        except Exception as e:
            logger.critical(
                f"Proposal failed to pass strict schema validation even after sanitization! "
                f"Falling back to NO_ACTION immediately. Error details: {e}"
            )
            p = NoActionProposal(
                action="no_action",
                reason=f"Auto-fallback triggered. Strict validation failed: {str(e)}",
            )
            import traceback

            traceback.print_exc()

        Path(output_file_path).write_text(p.model_dump_json(indent=2), encoding="utf-8")
        return p

    return finish


class SkillProposer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _skills_layer: SkillsLayer
    _wiki_layer: WikiLayer
    _raw_layer: RawLayer

    def __init__(self):
        self._model = init_chat_model(
            model=os.environ["SKILL_PROPOSER_MODEL"],
            model_provider="google_genai",
            temperature=float(os.environ["TEMPERATURE"]),
            vertexai=os.environ["GOOGLE_GENAI_USE_VERTEXAI"].lower() == "true",
            enterprise=os.environ["GOOGLE_GENAI_USE_ENTERPRISE"].lower() == "true",
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.environ["SKILL_PROPOSER_MODEL_LOCATION"],
            thinking_config={
                "thinking_level": os.environ["THINKING_LEVEL"],
                "include_thoughts": os.environ["INCLUDE_THOUGHTS"].lower() == "true",
            },
        )
        self._skills_layer = SkillsLayer()
        self._wiki_layer = WikiLayer()
        self._raw_layer = RawLayer()

    def _block_forbidden_files(self, request, handler):
        tool_name = request.tool_call.get("name", "")
        if tool_name in ("write_file", "edit_file", "delete"):
            return ToolMessage(
                content="Write, Edit, Delete actions are forbidden.",
                name=tool_name,
                tool_call_id=request.tool_call.get("id", "avoid"),
            )

        args = request.tool_call.get("args", {})
        raw_path = args.get("file_path") or args.get("path") or ""
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

        _full_blocked_files = [
            ".gitignore",
            ".gitattributes",
            ".gitmodules",
            ".DS_Store",
            "readme.md",
        ]
        if file_name.lower() in _full_blocked_files:
            logger.warning(
                f"Block forbidden file {tool_name} of {_full_blocked_files} at WikiMaintainer"
            )
            return ToolMessage(
                content="The {file_name} is protected and must NOT be read, written, or modified.",
                name=tool_name,
                tool_call_id=request.tool_call.get("id", "avoid"),
            )

        return handler(request)

    async def __call__(self, **kwargs):
        session_id = kwargs["session_id"]
        assert session_id, "session_id must be specified"

        task_id = kwargs["task_id"]
        assert task_id, "task_id must be specified"

        output_dir = kwargs["output_dir"]
        assert output_dir, "output_dir must be specified"
        output_abs_path = os.path.abspath(output_dir)

        traces_dir = kwargs["traces_dir"]
        assert os.path.exists(traces_dir)
        traces_abs_path = os.path.abspath(traces_dir)

        workspace_dir = kwargs["workspace_dir"]
        assert os.path.exists(workspace_dir)
        workspace_abs_path = os.path.abspath(workspace_dir)

        stream_mode = kwargs.get("stream_mode") == True

        traces_dict = self._raw_layer.read_traces(traces_abs_path)
        traces_str = str(traces_dict)
        first_human = next(
            (item for item in traces_dict if item.get("type") == "human"), None
        )
        task_desc = first_human["content"] if first_human else ""
        system_prompt = _SYSTEM_PROMPT.format(
            task_desc=task_desc,
            workspace_dir=workspace_abs_path,
        )
        logger.debug(f"system prompt:\n\n{system_prompt[:250]}...\n\n")
        backend = FilesystemBackend(root_dir=workspace_abs_path, virtual_mode=False)
        read_only_middleware = FilesystemMiddleware(
            backend=backend,
            tools=[
                "read_file",
                "ls",
                "glob",
                "grep",
            ],
        )
        created_finish_tool = _create_finish_tool(
            output_dir=Path(output_abs_path),
            session_id=session_id,
            task_id=task_id,
        )
        tools = [created_finish_tool]

        self._agent = create_deep_agent(
            model=self._model,
            backend=backend,
            middleware=[
                AwrapToolCall(self._block_forbidden_files),
                read_only_middleware,
            ],
            system_prompt=system_prompt,
            tools=tools,
        )
        logger.info(
            f"Run SkillProposer for traces:\n\n{traces_str[:100]}...\n\nTask:\n\n{task_desc[:100]}...\n\n"
        )
        messages = [
            {
                "role": "user",
                "content": f"""Finalize a proposal, here is the **task execution traces**:
{traces_str}""",
            }
        ]
        await run_deepagents(self._agent, messages, stream_mode)
        logger.success("SkillProposer done")


async def main(args):
    skill_proposer = SkillProposer()
    await skill_proposer(
        session_id=args.session_id,
        task_id=args.task_id,
        traces_dir=args.traces_dir,
        workspace_dir=args.workspace_dir,
        output_dir=args.output_dir,
        stream_mode=args.stream_mode,
    )


if __name__ == "__main__":

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--session_id",
        type=str,
        required=True,
        help="Session id",
    )
    parser.add_argument(
        "--task_id",
        type=str,
        required=True,
        help="Task id",
    )
    parser.add_argument(
        "--traces_dir",
        type=str,
        required=True,
        help="Inference traces directory",
    )
    parser.add_argument(
        "--workspace_dir",
        type=str,
        required=True,
        help="A workspace directory where we can find wiki/ and skills/ subdirectories",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        default="../output",
        help="Output directory",
    )
    parser.add_argument(
        "--stream_mode",
        action="store_true",
        help="Set for stream mode",
    )
    args = parser.parse_args()

    # python skill_proposer.py --session_id 38a619f7-7614-4473-bc53-a5a3f46c2b81 --task_id 1234455 --traces_dir ../output/38a619f7-7614-4473-bc53-a5a3f46c2b81/1234455 --workspace_dir ../workspace --output_dir ../output --stream_mode
    import asyncio

    asyncio.run(main(args))
