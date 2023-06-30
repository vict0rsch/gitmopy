"""
Utility functions and constants for ``gitmopy``.
"""
from os.path import expandvars
from pathlib import Path
from shutil import get_terminal_size
from textwrap import dedent
from typing import Dict, List, Union, Any

import typer
from InquirerPy.separator import Separator
from rich.console import Console
from yaml import safe_dump, safe_load

console = Console()
print = console.print


def resolve_path(path: Union[str, Path]) -> Path:
    """
    Resolve a path with ``expandvars``, ``expanduser`` and ``resolve``.

    Args:
        path (Union[str, Path]): Path to resolve.

    Returns:
        Path: Resolved (absolute) path.
    """
    return Path(expandvars(path)).expanduser().resolve()


APP_PATH = resolve_path(typer.get_app_dir("gitmopy", force_posix=True))
"""
Path to the application directory.
"""

CONFIG_PATH = APP_PATH / "config.yaml"
"""
Path to the configuration file.
"""

HISTORY_PATH = APP_PATH / "history.json"
"""
Path to the history file.
"""

USER_GITMOJIS_PATH = APP_PATH / "custom_gitmojis.json"
"""
Path to the user's gitmojis file.
"""

COLORS = {
    "r": "red",
    "g": "green3",
    "b": "dodger_blue3",
    "y": "yellow3",
    "o": "orange3",
    "p": "plum3",
}
"""
Rich colours for prints.
"""

_sentinels = {
    k: object() for k in ["stop", "restart", "cancelled", "sync", "no-branch"]
}
"""
Private constants
"""

DEFAULT_CHOICES = [
    {
        "value": "skip_scope",
        "name": "Skip commit scope",
        "default": False,
    },
    {
        "value": "skip_message",
        "name": "Skip commit message",
        "default": False,
    },
    {
        "value": "capitalize_title",
        "name": "Capitalize commit title",
        "default": True,
    },
    {
        "value": "enable_history",
        "name": "Remember commit history for auto-complete and emoji sorting",
        "default": True,
    },
]
"""
Choices for the setup prompt.
"""

DEFAULT_CONFIG = {c["value"]: c["default"] for c in DEFAULT_CHOICES}
"""
Default gitmopy configuration.
"""


def col(txt, color, bold=False):
    """
    Return a coloured string with Rich.

    Args:
        txt (str): String to colour.
        colour (str): Colour to use.
        bold (bool, optional): Whether to use bold font. Defaults to False.

    Returns:
        str: Coloured string.
    """
    return (
        f"[{COLORS[color]}]{txt}[/]" if not bold else f"[{COLORS[color]} bold]{txt}[/]"
    )


def load_config() -> Dict[str, bool]:
    """
    Load the configuration from ``${APP_PATH}/config.yaml``.

    Returns the default configuration if the file does not exist.

    Returns:
        Dict[str, bool]: User gitmopy configuration.
    """
    yaml_path = APP_PATH / "config.yaml"
    if yaml_path.exists():
        return {**DEFAULT_CONFIG, **safe_load(yaml_path.read_text())}
    return DEFAULT_CONFIG


def save_config(config: Dict[str, bool]) -> None:
    """
    Save the configuration to ``${APP_PATH}/config.yaml``.

    Creates the parent directory if it does not exist.

    Args:
        config (Dict[str, bool]): Current gitmopy configuration.
    """
    yaml_path = APP_PATH / "config.yaml"
    if not yaml_path.exists():
        print("[bold yellow] Creating config file [/bold yellow]", str(yaml_path))
    yaml_path.parent.mkdir(exist_ok=True)
    yaml_path.write_text(safe_dump(config))
    print("✅ Config updated")


def print_staged_files(staged: List[str]) -> None:
    """
    Print the currently staged files with Rich colours.

    Args:
        staged (List[str]): List of staged files paths.
    """
    nst = len(staged)
    s = "" if nst == 1 else "s"
    print(f"[green3]Currently {nst} staged file{s} for commit:[/green3]")
    for f in staged:
        print(f"  [grey66]- {f}[/grey66]")


def message_from_commit_dict(commit_dict: Dict[str, str]) -> str:
    r"""
    Create a commit message from a commit dictionary.

    Depending on whether ``scope`` is set, will look like

    * ``{emoji} ({scope}): {title}``
    * ``{emoji}: {title}``

    Then ``\n\n{message}`` is appended if a message is specified.


    Args:
        commit_dict (Dict[str, str]): Commit specs from the prompt.

    Returns:
        str: formatted commit message.
    """
    message = f"{commit_dict['emoji']} "
    if commit_dict["scope"]:
        message += f"({commit_dict['scope']}): "
    message += f"{commit_dict['title']}\n\n{commit_dict['message']}"
    return message.strip()


def choice_separator(title: str = "", width: int = 30, sep: str = "─") -> Separator:
    """
    Create an InquirerPy separator with a title.

    Args:
        title (str, optional): Title in-between separator characters.
            Defaults to ``""``.
        width (int, optional): Total length of sperator line. Defaults to 30.
        sep (str, optional): Character to use around the ``title``. Defaults to ``"─"``.

    Returns:
        Separator: _description_
    """
    assert sep
    assert width > 0
    if len(title) > width - 4:
        width = len(title) + 4

    first = (width - len(title)) // 2
    line = f"{sep * first} {title} {sep * (width - first - len(title) - 2)}"
    return Separator(line)


def safe_capitalize(s):
    """
    Capitalize a string if it is not empty, but keeps all-caps words.

    Example:
    ..code-block:: python

        >>> safe_capitalize("hello")
        "Hello"
        >>> safe_capitalize("HELLO")
        "HELLO"
        >>> "HELLO".capitalize()
        "Hello"

    Args:
        s (str): String to capitalize
    """
    if not s:
        return s
    if len(s) == 1:
        return s.upper()
    return s[0].upper() + s[1:]


def terminal_separator(margin=10):
    """
    Create a separator for the terminal.

    Returns:
        str: Terminal separator
    """
    total = get_terminal_size().columns
    sep = "─" * (total - 2 * margin)
    return f"{' ' * margin}{sep}{' ' * margin}"


def load_user_gitmojis() -> List[Dict[str, str]]:
    """
    Load custom gitmojis from ``${APP_PATH}/custom_gitmojis.yaml``.

    Returns:
        List[Dict[str, str]]: Custom gitmojis.
    """
    custom_emos = []
    try:
        if USER_GITMOJIS_PATH.exists():
            custom_emos = safe_load(USER_GITMOJIS_PATH.read_text()) or []
        else:
            USER_GITMOJIS_PATH.write_text(
                dedent(
                    """\
            # A file to add your own emojies. For instance, uncomment
            # the following lines to add new emojis to the list of suggestions
            # for when you commit:

            # - emoji: "🧫"
            #   description: Experimental code

            # - emoji: "💪"
            #   description: Add utility functions
            """
                )
            )
            custom_emos = []
        validate_user_emojis(custom_emos)
    except Exception as e:
        print(
            col(
                f"Error loading custom gitmojis from {str(USER_GITMOJIS_PATH)}, ignoring.",
                "red",
                True,
            )
        )
        print(str(e))
        custom_emos = []

    finally:
        return custom_emos


def validate_user_emojis(custom_emos: Any) -> List[Dict[str, str]]:
    """
    Validate user emojis.

    * Must be a list of dictionaries (possibly empty)
    * Each dictionary must have an ``emoji`` key and a ``description`` key
    * Each key must be a string
    * Each key must be non-empty

    Raises:
        ValueError: If any of the above conditions are not met.

    args:
        custom_emos (Any): User defined emojis.

    Returns:
        List[Dict[str, str]]: Validated emojis.
    """
    if not isinstance(custom_emos, list):
        raise ValueError("Custom gitmojis must be a list")

    for gitmoji in custom_emos:
        if not isinstance(gitmoji, dict):
            raise ValueError("Custom gitmojis must be a list of dictionaries")
        if "emoji" not in gitmoji:
            raise ValueError("Custom gitmojis must have an 'emoji' key")
        if "description" not in gitmoji:
            raise ValueError("Custom gitmojis must have a 'description' key")
        if not isinstance(gitmoji["emoji"], str):
            raise ValueError("Custom gitmojis must have a [b]string[b] 'emoji' key")
        if not isinstance(gitmoji["description"], str):
            raise ValueError(
                "Custom gitmojis must have a [b]string[b] 'description' key"
            )
        if not gitmoji["emoji"]:
            raise ValueError("Custom gitmojis must have a non-empty 'emoji' key")
        if not gitmoji["description"]:
            raise ValueError("Custom gitmojis must have a non-empty 'description' key")


# https://github.com/carloscuesta/gitmoji/blob/master/packages/gitmojis/src/gitmojis.json
GITMOJIS = [
    {
        "emoji": "🎨",
        "description": "Improve structure / format of the code.",
    },
    {
        "emoji": "⚡️",
        "description": "Improve performance.",
    },
    {
        "emoji": "🔥",
        "description": "Remove code or files.",
    },
    {
        "emoji": "🐛",
        "description": "Fix a bug.",
    },
    {
        "emoji": "🚑️",
        "description": "Critical hotfix.",
    },
    {
        "emoji": "✨",
        "description": "Introduce new features.",
    },
    {
        "emoji": "📝",
        "description": "Add or update documentation.",
    },
    {
        "emoji": "🚀",
        "description": "Deploy stuff.",
    },
    {
        "emoji": "💄",
        "description": "Add or update the UI and style files.",
    },
    {
        "emoji": "🎉",
        "description": "Begin a project.",
    },
    {
        "emoji": "✅",
        "description": "Add, update, or pass tests.",
    },
    {
        "emoji": "🔒️",
        "description": "Fix security issues.",
    },
    {
        "emoji": "🔐",
        "description": "Add or update secrets.",
    },
    {
        "emoji": "🔖",
        "description": "Release / Version tags.",
    },
    {
        "emoji": "🚨",
        "description": "Fix compiler / linter warnings.",
    },
    {
        "emoji": "🚧",
        "description": "Work in progress.",
    },
    {
        "emoji": "💚",
        "description": "Fix CI Build.",
    },
    {
        "emoji": "⬇️",
        "description": "Downgrade dependencies.",
    },
    {
        "emoji": "⬆️",
        "description": "Upgrade dependencies.",
    },
    {
        "emoji": "📌",
        "description": "Pin dependencies to specific versions.",
    },
    {
        "emoji": "👷",
        "description": "Add or update CI build system.",
    },
    {
        "emoji": "📈",
        "description": "Add or update analytics or track code.",
    },
    {
        "emoji": "♻️",
        "description": "Refactor code.",
    },
    {
        "emoji": "➕",
        "description": "Add a dependency.",
    },
    {
        "emoji": "➖",
        "description": "Remove a dependency.",
    },
    {
        "emoji": "🔧",
        "description": "Add or update configuration files.",
    },
    {
        "emoji": "🔨",
        "description": "Add or update development scripts.",
    },
    {
        "emoji": "🌐",
        "description": "Internationalization and localization.",
    },
    {
        "emoji": "✏️",
        "description": "Fix typos.",
    },
    {
        "emoji": "💩",
        "description": "Write bad code that needs to be improved.",
    },
    {
        "emoji": "⏪️",
        "description": "Revert changes.",
    },
    {
        "emoji": "🔀",
        "description": "Merge branches.",
    },
    {
        "emoji": "📦️",
        "description": "Add or update compiled files or packages.",
    },
    {
        "emoji": "👽️",
        "description": "Update code due to external API changes.",
    },
    {
        "emoji": "🚚",
        "description": "Move or rename resources (e.g.: files, paths, routes).",
    },
    {
        "emoji": "📄",
        "description": "Add or update license.",
    },
    {
        "emoji": "💥",
        "description": "Introduce breaking changes.",
    },
    {
        "emoji": "🍱",
        "description": "Add or update assets.",
    },
    {
        "emoji": "♿️",
        "description": "Improve accessibility.",
    },
    {
        "emoji": "💡",
        "description": "Add or update comments in source code.",
    },
    {
        "emoji": "🍻",
        "description": "Write code drunkenly.",
    },
    {
        "emoji": "💬",
        "description": "Add or update text and literals.",
    },
    {
        "emoji": "🗃️",
        "description": "Perform database related changes.",
    },
    {
        "emoji": "🔊",
        "description": "Add or update logs.",
    },
    {
        "emoji": "🔇",
        "description": "Remove logs.",
    },
    {
        "emoji": "👥",
        "description": "Add or update contributor(s).",
    },
    {
        "emoji": "🚸",
        "description": "Improve user experience / usability.",
    },
    {
        "emoji": "🏗️",
        "description": "Make architectural changes.",
    },
    {
        "emoji": "📱",
        "description": "Work on responsive design.",
    },
    {
        "emoji": "🤡",
        "description": "Mock things.",
    },
    {
        "emoji": "🥚",
        "description": "Add or update an easter egg.",
    },
    {
        "emoji": "🙈",
        "description": "Add or update a .gitignore file.",
    },
    {
        "emoji": "📸",
        "description": "Add or update snapshots.",
    },
    {
        "emoji": "⚗️",
        "description": "Perform experiments.",
    },
    {
        "emoji": "🔍️",
        "description": "Improve SEO.",
    },
    {
        "emoji": "🏷️",
        "description": "Add or update types.",
    },
    {
        "emoji": "🌱",
        "description": "Add or update seed files.",
    },
    {
        "emoji": "🚩",
        "description": "Add, update, or remove feature flags.",
    },
    {
        "emoji": "🥅",
        "description": "Catch errors.",
    },
    {
        "emoji": "💫",
        "description": "Add or update animations and transitions.",
    },
    {
        "emoji": "🗑️",
        "description": "Deprecate code that needs to be cleaned up.",
    },
    {
        "emoji": "🛂",
        "description": "Work on code related to authorization, roles and permissions.",
    },
    {
        "emoji": "🩹",
        "description": "Simple fix for a non-critical issue.",
    },
    {
        "emoji": "🧐",
        "description": "Data exploration/inspection.",
    },
    {
        "emoji": "⚰️",
        "description": "Remove dead code.",
    },
    {
        "emoji": "🧪",
        "description": "Add a failing test.",
    },
    {
        "emoji": "👔",
        "description": "Add or update business logic.",
    },
    {
        "emoji": "🩺",
        "description": "Add or update healthcheck.",
    },
    {
        "emoji": "🧱",
        "description": "Infrastructure related changes.",
    },
    {
        "emoji": "🧑‍💻",
        "description": "Improve developer experience.",
    },
    {
        "emoji": "💸",
        "description": "Add sponsorships or money related infrastructure.",
    },
    {
        "emoji": "🧵",
        "description": "Add or update code related to multithreading or concurrency.",
    },
    {
        "emoji": "🦺",
        "description": "Add or update code related to validation.",
    },
]
"""
List of emojis and their code and description according
to https://gitmoji.dev/
"""
