from rich.pretty import pprint as pp
from utils.stream_format import format_messages, show_message
from google.antigravity import Agent
from google.antigravity.types import Text, Thought, ToolCall, ToolResult
from google.antigravity.conversation.conversation import Conversation
import sys

_INVOKE_CONIFG = {"recursion_limit": 10000}


async def run_deepagents(agent, input_messages, stream_mode):
    if stream_mode:
        response = None
        seen_msg_ids = set()
        async for response in agent.astream(
            {"messages": input_messages},
            stream_mode="values",
            config=_INVOKE_CONIFG,
        ):
            for msg in response.get("messages", []):
                msg_id = getattr(msg, "id", None)
                if msg_id and msg_id not in seen_msg_ids:
                    seen_msg_ids.add(msg_id)
                    # pp(msg)
                    format_messages([msg])
    else:
        response = agent.invoke(
            {"messages": input_messages},
            config=_INVOKE_CONIFG,
        )
    return response


async def run_antigravity(config, message, stream_mode) -> Conversation:
    async with Agent(config) as agent:
        if stream_mode:
            response = await agent.chat(message)
            async for chunk in response.chunks:
                if isinstance(chunk, Text):
                    show_message(chunk.text, "✨ Assistant", border_style="bold green")
                elif isinstance(chunk, Thought):
                    show_message(chunk.text, "🧠 Thought", border_style="bold blue")
                elif isinstance(chunk, ToolCall):
                    show_message(
                        f"""Name: {chunk.name}
Args:
    {chunk.args}
""",
                        "Tool Call",
                        border_style="bold cyan",
                    )
                elif isinstance(chunk, ToolResult):
                    show_message(
                        f"""Name: {chunk.name}
Results:
    {chunk.result}
    
Error:
    {chunk.error}
Exception:
    {chunk.exception}
""",
                        "Tool Result",
                        border_style="bold magenta",
                    )
                else:
                    pass
                sys.stdout.flush()
            return agent.conversation
        else:
            response = await agent.chat(message)
            return agent.conversation
