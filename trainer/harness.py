import json
import os
from argparse import ArgumentParser
from pathlib import Path

from layers.raw_layer import RawLayer
from layers.skills_layer import SkillsLayer
from layers.wiki_layer import WikiLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from skill_proposer import (
    CreateSkillProposal,
    NoActionProposal,
    PatchOperation,
    PatchSkillProposal,
)


class Harness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _skills_layer: SkillsLayer
    _wiki_layer: WikiLayer
    _raw_layer: RawLayer

    def __init__(self):
        self._raw_layer = RawLayer()

    def reject(self):
        pass

    def accept(self):
        pass

    def update(self):
        pass

    def _on_create(
        self,
        skills_dir_path: Path,
        create_skill_proposal: CreateSkillProposal,
    ):
        skill_location = os.path.join(str(skills_dir_path), create_skill_proposal.name)
        skill_md = os.path.join(skill_location, "SKILL.md")
        purpose_md = os.path.join(skill_location, "PURPOSE.md")
        Path(skill_md).write_text(create_skill_proposal.skill_md, encoding="utf-8")
        logger.success(f"Created or overwritten {skill_md}")
        Path(purpose_md).write_text(create_skill_proposal.purpose_md, encoding="utf-8")
        logger.success(f"Create or overwritten {purpose_md}")

    def _on_patch(
        self,
        skills_dir_path: Path,
        patch_skill_proposal: PatchSkillProposal,
    ):
        skill_location = os.path.join(str(skills_dir_path), patch_skill_proposal.name)
        skill_md = os.path.join(skill_location, "SKILL.md")
        purpose_md = os.path.join(skill_location, "PURPOSE.md")

        current_skill_md = Path(skill_md).read_text(encoding="utf-8")
        current_purpose_md = Path(purpose_md).read_text(encoding="utf-8")
        for edit in patch_skill_proposal.edits:
            if edit.file == "SKILL.md":
                try:
                    current_skill_md = self._apply_edit(current_skill_md, edit)
                except ValueError as e:
                    logger.error(f"Failed on patching SKILL.md: {e}")
            if edit.file == "PURPOSE.md":
                try:
                    current_purpose_md = self._apply_edit(current_purpose_md, edit)
                except ValueError as e:
                    logger.error(f"Failed on patching PURPOSE.md: {e}")
        Path(skill_md).write_text(current_skill_md, encoding="utf-8")
        logger.success(f"Created or overwritten {skill_md}")
        Path(purpose_md).write_text(current_purpose_md, encoding="utf-8")
        logger.success(f"Created or overwritten {purpose_md}")

    def _apply_edit(self, original_text: str, edit: PatchOperation) -> str:
        target = edit.target
        new_content = edit.content
        match edit.op:
            case "replace":
                if not target or target not in original_text:
                    raise ValueError(f"Replace failed: NO target: '{target}'")
                return original_text.replace(target, new_content, 1)

            case "insert_after" | "insert":
                if not target or target not in original_text:
                    raise ValueError(f"Insert failed: NO target: '{target}'")
                idx = original_text.find(target) + len(target)
                prefix = "\n" if not new_content.startswith("\n") else ""
                return original_text[:idx] + prefix + new_content + original_text[idx:]
            case "append":
                separator = "\n\n" if not original_text.endswith("\n") else "\n"
                return original_text + separator + new_content

            case _:
                raise ValueError(f"Cannot identify op: {edit.op}")

    def apply(self, proposal_path: str, skills_dir: str):
        proposal_abs_path = os.path.abspath(proposal_path)
        skills_dir_abs_path = os.path.abspath(skills_dir)
        with open(proposal_abs_path, "r", encoding="utf-8") as f:
            j = json.load(f)
            if not isinstance(j, dict):
                proposal = NoActionProposal(
                    reason=f"Payload is not a JSON object: {type(j)}"
                )
            else:
                action = str(j.get("action", "")).strip().lower()
                try:
                    if action in ("create", "created", "new", "make"):
                        proposal = CreateSkillProposal.model_validate(j)
                        self._on_create(Path(skills_dir_abs_path), proposal)
                        logger.success(f"Harness invoked action {action}")
                    elif action in ("patch", "patched", "update", "updated", "edit"):
                        proposal = PatchSkillProposal.model_validate(j)
                        self._on_patch(Path(skills_dir_abs_path), proposal)
                        logger.success(f"Harness invoked action {action}")
                    elif action in (
                        "no_action",
                        "noaction",
                        "none",
                        "no-action",
                        "nothing",
                    ):
                        proposal = NoActionProposal.model_validate(j)
                        logger.success(
                            f"Harness does nothing, because action is {action}"
                        )
                    else:
                        proposal = NoActionProposal(
                            reason=f"Unrecognized action '{action}' in proposal payload."
                        )
                        logger.warning(
                            "Harness cannot identify any action, fallback to NoActionProposal"
                        )
                except Exception as e:
                    proposal = NoActionProposal(
                        reason=f"Failed to validate {action} proposal schema: {e}"
                    )
                    logger.critical(
                        "Harness gets error while applying, fallback to NoActionProposal"
                    )


async def main(args):
    harness = Harness()
    skills_dir = os.path.join(args.workspace_dir, "skills")
    harness.apply(
        proposal_path=args.proposal_path,
        skills_dir=skills_dir,
    )


if __name__ == "__main__":
    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--proposal_path",
        type=str,
        required=True,
        help="The path of proposal.json",
    )
    parser.add_argument(
        "--workspace_dir",
        type=str,
        required=True,
        help="A workspace directory where we can find wiki/ and skills/ subdirectories",
    )
    args = parser.parse_args()

    # python harness.py --proposal_path ../output/38a619f7-7614-4473-bc53-a5a3f46c2b81/1234455/proposal.json --workspace_dir ../workspace
    import asyncio

    asyncio.run(main(args))
