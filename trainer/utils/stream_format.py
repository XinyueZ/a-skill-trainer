import json
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.text import Text

console = Console()


def pp(obj: Any, log_file: str):
    # append to log file
    with open(log_file, "a", encoding="utf-8") as f:
        console = Console(file=f)
        pprint(obj, console=console)


def format_message_content(message):
    """Convert message content to displayable string"""
    parts = []
    tool_calls_processed = False

    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            try:
                if isinstance(item, str):
                    parts.append(f"✨   {item}")
                elif item.get("type") == "text":
                    parts.append(f"✨   {item['text']}")
                elif item.get("type") == "thinking":
                    parts.append(f"🧠   {item['thinking']}")
                elif item.get("type") == "tool_use":
                    parts.append(f"🔧   Tool Call: {item['name']}")
                    parts.append(
                        f"         Args: {json.dumps(item['input'], indent=2)}"
                    )
                    parts.append(f"         ID: {item.get('id', 'N/A')}")
                    tool_calls_processed = True
            except Exception as e:
                import traceback

                logger.error(f"Error: {e}")
                logger.error(traceback.format_exc())
    else:
        parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if (
        not tool_calls_processed
        and hasattr(message, "tool_calls")
        and message.tool_calls
    ):
        for tool_call in message.tool_calls:
            try:
                parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
                parts.append(f"   Args: {json.dumps(tool_call['args'], indent=2)}")
                parts.append(f"   ID: {tool_call['id']}")
            except Exception as e:
                import traceback

                logger.error(f"Error: {e}")
                logger.error(traceback.format_exc())

    return "\n".join(parts)


def format_messages(messages):
    """Format and display a list of messages with Rich formatting"""
    for m in messages:
        try:
            msg_type = m.__class__.__name__.replace("Message", "")
            content = format_message_content(m)

            if msg_type.lower() == "human":
                console.print(Panel(content, title="🧑 Human", border_style="blue"))
            elif msg_type.lower() == "ai":
                console.print(
                    Panel(content, title="🤖 Assistant", border_style="green")
                )
            elif msg_type.lower() == "tool":
                console.print(
                    Panel(content, title="🔧 Tool Output", border_style="yellow")
                )
            elif msg_type.lower() == "remove":
                console.print(
                    Panel(f"ID: {m.id}", title="🔥 Remove message", border_style="red")
                )
            else:
                console.print(
                    Panel(content, title=f"📝 {msg_type}", border_style="white")
                )
        except Exception as e:
            import traceback

            logger.error(f"Error: {e}")
            logger.error(traceback.format_exc())


def format_message(messages):
    """Alias for format_messages for backward compatibility"""
    return format_messages(messages)


def show_message(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """
    Display a prompt with rich formatting and XML tag highlighting.

    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    # Create a formatted display of the prompt
    try:
        formatted_text = Text(prompt_text)
        formatted_text.highlight_regex(
            r"<[^>]+>", style="bold blue"
        )  # Highlight XML tags
        formatted_text.highlight_regex(
            r"##[^#\n]+", style="bold magenta"
        )  # Highlight headers
        formatted_text.highlight_regex(
            r"###[^#\n]+", style="bold cyan"
        )  # Highlight sub-headers

        # Display in a panel for better presentation
        console.print(
            Panel(
                formatted_text,
                title=f"[bold green]{title}[/bold green]",
                border_style=border_style,
                padding=(1, 2),
            )
        )
    except Exception as e:
        import traceback

        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
