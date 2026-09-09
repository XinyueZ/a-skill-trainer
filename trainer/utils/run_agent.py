from rich.pretty import pprint as pp
from utils.stream_format import format_messages

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
