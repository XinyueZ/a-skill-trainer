import json
import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path

from layers.raw_layer import RawLayer

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

    _raw_layer: RawLayer

    _action: str
    _skill_name: str
    _diff: str
    _proposal_relation: str
    _outcome: str

    def __init__(self):
        self._raw_layer = RawLayer()

    def _on_create(
        self,
        skills_dir_path: Path,
        create_skill_proposal: CreateSkillProposal,
    ):
        skill_location = os.path.join(str(skills_dir_path), create_skill_proposal.name)
        skill_md_path = os.path.join(skill_location, "SKILL.md")
        purpose_md_path = os.path.join(skill_location, "PURPOSE.md")

        p = Path(skill_md_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(create_skill_proposal.skill_md, encoding="utf-8")
        logger.success(f"Created or overwritten {skill_md_path}")

        p = Path(purpose_md_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(create_skill_proposal.purpose_md, encoding="utf-8")
        logger.success(f"Create or overwritten {purpose_md_path}")

        # part of Update information
        self._proposal_relation = create_skill_proposal.purpose_md

    def _on_patch(
        self,
        skills_dir_path: Path,
        patch_skill_proposal: PatchSkillProposal,
    ):
        skill_location = os.path.join(str(skills_dir_path), patch_skill_proposal.name)
        skill_md_path = os.path.join(skill_location, "SKILL.md")
        purpose_md_path = os.path.join(skill_location, "PURPOSE.md")

        current_skill_md = Path(skill_md_path).read_text(encoding="utf-8")
        current_purpose_md = Path(purpose_md_path).read_text(encoding="utf-8")
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
        Path(skill_md_path).write_text(current_skill_md, encoding="utf-8")
        logger.success(f"Created or overwritten {skill_md_path}")
        Path(purpose_md_path).write_text(current_purpose_md, encoding="utf-8")
        logger.success(f"Created or overwritten {purpose_md_path}")

        # part of Update information
        self._proposal_relation = current_purpose_md

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
                # part of Update information
                self._skill_name = str(j.get("name", "")).strip().lower()
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
                    import traceback

                    traceback.print_exc()
                # part of Update information
                self._action = action

    def get_diff(self, workspace_dir: str) -> str:
        workspace_abs_dir_path = os.path.abspath(workspace_dir)
        cmd = f"git -C {workspace_abs_dir_path} diff HEAD -- skills"
        logger.debug(f"Seek diff via `{cmd}`")
        output = subprocess.check_output(cmd, shell=True, text=True)
        logger.success(f"Δ  Diff:\n\n{output[:500]}...\n\n")

        # part of Update information
        self._diff = output
        return output

    def reject(self, workspace_dir: str, skill_dir: str):
        workspace_dir_abs_path = os.path.abspath(workspace_dir)
        skill_dir_abs_path = os.path.abspath(skill_dir)

        # restore SKILL.md
        cmd = f"git -C {workspace_dir_abs_path} checkout HEAD -- skills"
        logger.debug(f"Seek checkout via `{cmd}`")
        output = subprocess.check_output(cmd, shell=True, text=True)
        logger.success(f"🅰️  Rejected(checkout):\n\n{output[:500]}...\n\n")

        # restore PURPOSE.md
        cmd = f"git -C {skill_dir_abs_path} clean -fd"
        logger.debug(f"Seek clean via `{cmd}`")
        output = subprocess.check_output(cmd, shell=True, text=True)
        logger.success(f"🅱️  Rejected(clean -fd):\n\n{output[:500]}...\n\n")

        # part of Update information
        self._outcome = "REJECTED"
        return output

    def accept(self, workspace_dir: str):
        prefix = "[WIKISKILL-ACCEPTED]"
        workspace_abs_dir_path = os.path.abspath(workspace_dir)

        # add skills/
        cmd = f"git -C {workspace_abs_dir_path} add -- skills"
        logger.debug(f"Seek add via `{cmd}`")
        output = subprocess.check_output(cmd, shell=True, text=True)
        logger.success(f"🔒 Accepted(add):\n\n{output[:500]}...\n\n")

        # commit skills/
        check_staged = subprocess.run(
            ["git", "-C", workspace_abs_dir_path, "diff", "--staged", "--", "skills"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not check_staged.stdout.strip():
            logger.warning("No staged changes in skills/ to commit. Skip commit.")
            self._outcome = "ACCEPTED"
            return "No changes to commit"

        commit_msg = f"{prefix}: {self._skill_name}"
        cmd_commit = ["git", "-C", workspace_abs_dir_path, "commit", "-m", commit_msg]
        logger.debug(f"Seek commit via `{' '.join(cmd_commit)}`")
        result = subprocess.run(cmd_commit, capture_output=True, text=True, check=True)
        output = result.stdout
        logger.success(f"💾 Accepted(commit):\n\n{output[:500]}...\n\n")

        # part of Update information
        self._outcome = "ACCEPTED"
        return output

    def accept_or_reject(self, workspace_dir: str, skill_dir: str, reject: bool):
        workspace_dir_abs_path = os.path.abspath(workspace_dir)
        skill_dir_abs_path = os.path.abspath(skill_dir)
        if reject:
            self.reject(workspace_dir_abs_path, skill_dir_abs_path)
        else:
            self.accept(workspace_dir_abs_path)

    def update(
        self,
        wiki_dir: str,
        feedback: str,
        iteration: int,
    ):
        wiki_abs_dir_path = os.path.abspath(wiki_dir)
        skill_impact_md_file_path = os.path.join(wiki_abs_dir_path, "skill-impact.md")
        headline = "# Skill Evolution Impact Tracker"
        feedback = feedback or "N/A"
        proposal_relation = self._proposal_relation or "N/A"
        reco = f"""## Iteration {iteration}: {self._action} {self._skill_name} -> {self._outcome}

- **Proposal Rationale**: {proposal_relation}
- **Feedback**: {feedback}
- **Git Diff**:
```diff
{self._diff}
``` 
"""
        if os.path.getsize(skill_impact_md_file_path) == 0:
            with open(skill_impact_md_file_path, "a", encoding="utf-8") as f:
                f.write(headline + "\n\n" + reco + "\n\n---\n\n")
        else:
            with open(skill_impact_md_file_path, "a", encoding="utf-8") as f:
                f.write(reco + "\n\n---\n\n")


async def main(args):
    harness = Harness()

    workspace_dir_abs_path = os.path.abspath(args.workspace_dir)
    skills_dir = os.path.join(workspace_dir_abs_path, "skills")
    wiki_dir = os.path.join(workspace_dir_abs_path, "wiki")
    proposal_abs_path = os.path.abspath(args.proposal_path)

    harness.apply(proposal_path=proposal_abs_path, skills_dir=skills_dir)
    harness.get_diff(workspace_dir_abs_path)

    harness.accept_or_reject(workspace_dir_abs_path, skills_dir, args.reject)
    harness.update(
        wiki_dir,
        feedback=args.feedback,
        iteration=args.iteration,
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
    parser.add_argument(
        "--iteration",
        type=int,
        required=False,
        help="Set iteration",
    )
    parser.add_argument(
        "--reject",
        action="store_true",
        help="Set, if reject a proposal at commandline mode",
    )
    parser.add_argument(
        "--feedback",
        type=str,
        required=False,
        help="A feedback on the applied proposal",
    )
    args = parser.parse_args()

    # python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/5e6b67b3-7c7e-4c48-aac8-06cdb0c8a2ba/1/proposal.json  --reject --iteration 0 --feedback="It is better to use some scripts to support"
    # python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/48f92222-b2b0-4ad1-9e87-0709a48e1609/1/proposal.json  --iteration 1 --feedback="Make the scripts more robust"
    # python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/63f73e44-30ad-4f8f-8d78-d944c3c77426/1/proposal.json  --iteration 2 --feedback="Add reuqirments (libs strong versions) that the scripts can work with"
    # python trainer/harness.py --workspace_dir ./workspace --proposal_path ./output/63f73e44-30ad-4f8f-8d78-d944c3c77426/1/proposal.json  --iteration 3
    import asyncio

    asyncio.run(main(args))
