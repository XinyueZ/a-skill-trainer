import os
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from layers.raw_layer import RawLayer
from layers.wiki_layer import WikiLayer
from loguru import logger
from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv

load_dotenv()
_INVOKE_CONIFG = {"recursion_limit": 10000}
_PROMPT = """
You are a Wiki Maintainer Agent for an LLM skill evolution system.
Your job is to maintain a structured knowledge base (wiki) directly on the local filesystem that documents patterns observed during agent execution -- both successes and failures. You must perform DEEP ANALYSIS of execution logs to identify root causes, not just surface-level symptoms.

## Workspace & Wiki Structure

**CRITICAL**: Your workspace directory is located at `{workspace_dir}`. You must always perform all operations within the `wiki/` subdirectory of this path.
**CRITICAL**: DON'T CHANGE ANY README.MD FILES WHICH ARE THE DESCRIPTIONS OF THE WORKSPACE STUFFS.

The wiki is organized on disk as:
- `wiki/index.md` -- Concise catalog of known patterns (one line per pattern)
- `wiki/log.md` -- Chronological evolution log (iterations, scores, accept/reject)
- `wiki/skill-impact.md` -- Record of which skills were tried and their outcomes
- `wiki/patterns/` -- One page per pattern with detailed evidence and analysis (e.g., `wiki/patterns/pattern-name.md`)

## Your Input

1. Execution traces from the latest iteration -- including full agent execution logs showing what actions the agent took, what commands it ran, and what environment feedback it observed:

{traces}

2. The current wiki context (index, log, pattern pages) located on the local filesystem under `{workspace_dir}/wiki/`, accessible via your built-in filesystem tools.

## Available Filesystem Tools

You have direct access to the local filesystem through built-in tools:
- `ls(path)`: List directory contents to inspect the wiki structure.
- `glob(pattern)`: Find files matching patterns (e.g., `wiki/patterns/*.md`).
- `read_file(path, offset, limit)`: Read current wiki pages, index, log, or trace files.
- `write_file(path, content)`: Create new pattern pages, or write full updated content to `wiki/index.md`.
- `edit_file(path, old_string, new_string, replace_all)`: Perform precise in-place edits on existing files.
- `grep(pattern, path)`: Search for existing keywords, pattern topics, or error signatures across the wiki.

## Execution & Maintenance Workflow

Follow this step-by-step workflow during each evolution cycle:

1. **Analyze Execution Traces**:
   - Deeply inspect the execution traces provided in `{traces}`.
   - Perform root-cause analysis (see Deep Trace Analysis guidelines below).

2. **Inspect Existing Wiki State**:
   - Use `glob` or `ls` (e.g., `wiki/patterns/`) and `read_file("wiki/index.md")` within `{workspace_dir}` to understand current state.
   - Use `grep` or `read_file` on related pattern files to prevent duplicates.

3. **Create or Update Patterns**:
   - **For New Patterns**: Use `write_file("wiki/patterns/<pattern-name>.md", content)` to create the pattern document following the documentation rules.
   - **For Existing Patterns**: Use `edit_file` (or `write_file`) to enrich existing patterns with new evidence, updated fixes, or refined root cause analysis.

4. **Update `wiki/index.md` (MANDATORY)**:
   - You MUST ensure `wiki/index.md` reflects all current patterns, including any newly added or updated ones.
   - Read `wiki/index.md` first, update the catalog, and write the complete, updated index back using `write_file`.

5. **Append to `wiki/log.md` (MANDATORY)**:
   - You MUST record a brief chronological summary of this iteration's findings, decisions, and file changes into `wiki/log.md` using `edit_file` or `write_file`.

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

The `wiki/index.md` entries are the MOST IMPORTANT part of the wiki because they determine whether inference agents will read the full pattern pages.
Each index entry MUST follow this format:
- `[pattern-name](wiki/patterns/pattern-name.md): PROBLEM + ROOT CAUSE + FIX in one or two sentences.`

The description must be specific enough that an agent can judge relevance without reading the full page. Include the problem, root cause, AND solution.
"""


class WikiMaintaincer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _raw_layer: RawLayer
    _wiki_layer: WikiLayer

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

    def __call__(self, **kwargs):
        traces_dir = kwargs["traces_dir"]
        assert os.path.exists(traces_dir)

        workspace_dir = kwargs["workspace_dir"]
        assert os.path.exists(workspace_dir)

        traces_dict = self._raw_layer.read_traces(traces_dir)
        traces_str = str(traces_dict)
        prompt = _PROMPT.format(workspace_dir=workspace_dir, traces=str(traces_str))
        backend = FilesystemBackend(root_dir=workspace_dir, virtual_mode=False)
        self._agent = create_deep_agent(model=self._model, backend=backend)
        logger.info(
            f"Run WikiMaintainer, at {workspace_dir}, for traces:\n\n{traces_str[:100]}...\n\n"
        )
        response = self._agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": prompt},
                ]
            },
            config=_INVOKE_CONIFG,
        )
        logger.success(f"WikiMaintainer done")


if __name__ == "__main__":
    # read cli args
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
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
        help="Wiki directory (current state)",
    )

    args = parser.parse_args()

    # python wiki_maintainer.py --traces_dir ../output/746218fa-ce09-4e7e-bab5-f42b58646eef/1234455 --workspace_dir ../workspace
    # python wiki_maintainer.py --traces_dir ../output/dd1b9e3a-116e-4f05-8579-ffc27c09cfdb/1234455 --workspace_dir ../workspace
    # python wiki_maintainer.py --traces_dir ../output/e7e2f1ed-5274-4d13-bc39-0e967b0d3650/1234455 --workspace_dir ../workspace

    wiki_maintainer = WikiMaintaincer()
    wiki_maintainer(traces_dir=args.traces_dir, workspace_dir=args.workspace_dir)
