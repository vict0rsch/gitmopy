"""
Utility functions and constants for ``gitmopy``.
"""

from os.path import expandvars
from pathlib import Path
from shutil import get_terminal_size
from textwrap import dedent
from typing import Any, Dict, List, Union

import wcwidth
from InquirerPy.separator import Separator
from rich.console import Console
from yaml import safe_dump, safe_load

from gitmopy.constants import (
    APP_PATH,
    COLORS,
    DEFAULT_CHOICES,
    DEFAULT_CONFIG,
    USER_EMOJIS_PATH,
)

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


def check_config(config: Dict[str, Union[bool, str]]) -> None:
    """
    Check that the user configuration is valid.

    Args:
        config (Dict[str, Union[bool, str]]): Current gitmopy configuration
            that should be saved


    Raises:
        ValueError: Unknown config key
        ValueError: Wrong config value type
    """
    assert isinstance(config, dict)
    conf = {**DEFAULT_CONFIG, **config}
    for k, v in config.items():
        if k not in DEFAULT_CONFIG:
            raise ValueError(f"Unknown config key {k}")
        if not isinstance(v, type(DEFAULT_CONFIG[k])):
            raise ValueError(
                f"Config key {k} must be of type {type(DEFAULT_CONFIG[k])}"
            )
    return conf


def save_config(config: Dict[str, Union[bool, str]]) -> None:
    """
    Save the configuration to ``${APP_PATH}/config.yaml``.

    Creates the parent directory if it does not exist.

    Args:
        config (Dict[str, Union[bool, str]]): Current gitmopy configuration.
    """
    yaml_path = APP_PATH / "config.yaml"
    if not yaml_path.exists():
        print("[bold yellow] Creating config file [/bold yellow]", str(yaml_path))
    yaml_path.parent.mkdir(exist_ok=True)
    check_config(config)
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
        if USER_EMOJIS_PATH.exists():
            custom_emos = safe_load(USER_EMOJIS_PATH.read_text()) or []
        else:
            USER_EMOJIS_PATH.write_text(
                dedent(
                    """\
            # A file to add your own emojies.

            # For instance, uncomment the following lines to add new emojis
            # to the list of suggestions for when you commit:

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
                f"Error loading custom gitmojis from {str(USER_EMOJIS_PATH)},"
                + " ignoring.",
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


def clear_line_and_move_up():
    """
    Clear the current line and move up one line in the terminal.
    """
    import sys

    sys.stdout.write("\033[2K\033[A")
    sys.stdout.flush()


def standard_width_emoji(emoji: str, to=2) -> str:
    """
    Return a standard width emoji of width 2.
    """
    assert to >= 2
    if len(emoji) > 1:
        emoji = emoji[0]
    return emoji + " " * (to - wcwidth.wcwidth(emoji))


def set_start_options():
    """
    Set the options for the default commit arguments automatically from the ``gitmopy commit`` command's signature.
    """
    global DEFAULT_CHOICES
    import inspect

    from gitmopy.cli import commit

    start_idx = next(
        i for i, c in enumerate(DEFAULT_CHOICES) if c["value"] == "default_commit_flags"
    )

    DEFAULT_CHOICES[start_idx]["options"] = sorted(
        arg
        for arg in inspect.signature(commit).parameters.keys()
        if arg not in {"repo", "remote"}
    )
