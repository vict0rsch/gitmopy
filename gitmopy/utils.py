"""
Utility functions and constants for ``gitmopy``.
"""
from os.path import expandvars
from pathlib import Path
from shutil import get_terminal_size
from typing import Dict, List, Union

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


# https://github.com/carloscuesta/gitmoji/blob/master/packages/gitmojis/src/gitmojis.json
GITMOJIS = [
    {
        "emoji": "🎨",
        "entity": "&#x1f3a8;",
        "code": ":art:",
        "description": "Improve structure / format of the code.",
        "name": "art",
        "semver": "",
    },
    {
        "emoji": "⚡️",
        "entity": "&#x26a1;",
        "code": ":zap:",
        "description": "Improve performance.",
        "name": "zap",
        "semver": "patch",
    },
    {
        "emoji": "🔥",
        "entity": "&#x1f525;",
        "code": ":fire:",
        "description": "Remove code or files.",
        "name": "fire",
        "semver": "",
    },
    {
        "emoji": "🐛",
        "entity": "&#x1f41b;",
        "code": ":bug:",
        "description": "Fix a bug.",
        "name": "bug",
        "semver": "patch",
    },
    {
        "emoji": "🚑️",
        "entity": "&#128657;",
        "code": ":ambulance:",
        "description": "Critical hotfix.",
        "name": "ambulance",
        "semver": "patch",
    },
    {
        "emoji": "✨",
        "entity": "&#x2728;",
        "code": ":sparkles:",
        "description": "Introduce new features.",
        "name": "sparkles",
        "semver": "minor",
    },
    {
        "emoji": "📝",
        "entity": "&#x1f4dd;",
        "code": ":memo:",
        "description": "Add or update documentation.",
        "name": "memo",
        "semver": "",
    },
    {
        "emoji": "🚀",
        "entity": "&#x1f680;",
        "code": ":rocket:",
        "description": "Deploy stuff.",
        "name": "rocket",
        "semver": "",
    },
    {
        "emoji": "💄",
        "entity": "&#ff99cc;",
        "code": ":lipstick:",
        "description": "Add or update the UI and style files.",
        "name": "lipstick",
        "semver": "patch",
    },
    {
        "emoji": "🎉",
        "entity": "&#127881;",
        "code": ":tada:",
        "description": "Begin a project.",
        "name": "tada",
        "semver": "",
    },
    {
        "emoji": "✅",
        "entity": "&#x2705;",
        "code": ":white_check_mark:",
        "description": "Add, update, or pass tests.",
        "name": "white-check-mark",
        "semver": "",
    },
    {
        "emoji": "🔒️",
        "entity": "&#x1f512;",
        "code": ":lock:",
        "description": "Fix security issues.",
        "name": "lock",
        "semver": "patch",
    },
    {
        "emoji": "🔐",
        "entity": "&#x1f510;",
        "code": ":closed_lock_with_key:",
        "description": "Add or update secrets.",
        "name": "closed-lock-with-key",
        "semver": "",
    },
    {
        "emoji": "🔖",
        "entity": "&#x1f516;",
        "code": ":bookmark:",
        "description": "Release / Version tags.",
        "name": "bookmark",
        "semver": "",
    },
    {
        "emoji": "🚨",
        "entity": "&#x1f6a8;",
        "code": ":rotating_light:",
        "description": "Fix compiler / linter warnings.",
        "name": "rotating-light",
        "semver": "",
    },
    {
        "emoji": "🚧",
        "entity": "&#x1f6a7;",
        "code": ":construction:",
        "description": "Work in progress.",
        "name": "construction",
        "semver": "",
    },
    {
        "emoji": "💚",
        "entity": "&#x1f49a;",
        "code": ":green_heart:",
        "description": "Fix CI Build.",
        "name": "green-heart",
        "semver": "",
    },
    {
        "emoji": "⬇️",
        "entity": "⬇️",
        "code": ":arrow_down:",
        "description": "Downgrade dependencies.",
        "name": "arrow-down",
        "semver": "patch",
    },
    {
        "emoji": "⬆️",
        "entity": "⬆️",
        "code": ":arrow_up:",
        "description": "Upgrade dependencies.",
        "name": "arrow-up",
        "semver": "patch",
    },
    {
        "emoji": "📌",
        "entity": "&#x1F4CC;",
        "code": ":pushpin:",
        "description": "Pin dependencies to specific versions.",
        "name": "pushpin",
        "semver": "patch",
    },
    {
        "emoji": "👷",
        "entity": "&#x1f477;",
        "code": ":construction_worker:",
        "description": "Add or update CI build system.",
        "name": "construction-worker",
        "semver": "",
    },
    {
        "emoji": "📈",
        "entity": "&#x1F4C8;",
        "code": ":chart_with_upwards_trend:",
        "description": "Add or update analytics or track code.",
        "name": "chart-with-upwards-trend",
        "semver": "patch",
    },
    {
        "emoji": "♻️",
        "entity": "&#x267b;",
        "code": ":recycle:",
        "description": "Refactor code.",
        "name": "recycle",
        "semver": "",
    },
    {
        "emoji": "➕",
        "entity": "&#10133;",
        "code": ":heavy_plus_sign:",
        "description": "Add a dependency.",
        "name": "heavy-plus-sign",
        "semver": "patch",
    },
    {
        "emoji": "➖",
        "entity": "&#10134;",
        "code": ":heavy_minus_sign:",
        "description": "Remove a dependency.",
        "name": "heavy-minus-sign",
        "semver": "patch",
    },
    {
        "emoji": "🔧",
        "entity": "&#x1f527;",
        "code": ":wrench:",
        "description": "Add or update configuration files.",
        "name": "wrench",
        "semver": "patch",
    },
    {
        "emoji": "🔨",
        "entity": "&#128296;",
        "code": ":hammer:",
        "description": "Add or update development scripts.",
        "name": "hammer",
        "semver": "",
    },
    {
        "emoji": "🌐",
        "entity": "&#127760;",
        "code": ":globe_with_meridians:",
        "description": "Internationalization and localization.",
        "name": "globe-with-meridians",
        "semver": "patch",
    },
    {
        "emoji": "✏️",
        "entity": "&#59161;",
        "code": ":pencil2:",
        "description": "Fix typos.",
        "name": "pencil2",
        "semver": "patch",
    },
    {
        "emoji": "💩",
        "entity": "&#58613;",
        "code": ":poop:",
        "description": "Write bad code that needs to be improved.",
        "name": "poop",
        "semver": "",
    },
    {
        "emoji": "⏪️",
        "entity": "&#9194;",
        "code": ":rewind:",
        "description": "Revert changes.",
        "name": "rewind",
        "semver": "patch",
    },
    {
        "emoji": "🔀",
        "entity": "&#128256;",
        "code": ":twisted_rightwards_arrows:",
        "description": "Merge branches.",
        "name": "twisted-rightwards-arrows",
        "semver": "",
    },
    {
        "emoji": "📦️",
        "entity": "&#1F4E6;",
        "code": ":package:",
        "description": "Add or update compiled files or packages.",
        "name": "package",
        "semver": "patch",
    },
    {
        "emoji": "👽️",
        "entity": "&#1F47D;",
        "code": ":alien:",
        "description": "Update code due to external API changes.",
        "name": "alien",
        "semver": "patch",
    },
    {
        "emoji": "🚚",
        "entity": "&#1F69A;",
        "code": ":truck:",
        "description": "Move or rename resources (e.g.: files, paths, routes).",
        "name": "truck",
        "semver": "",
    },
    {
        "emoji": "📄",
        "entity": "&#1F4C4;",
        "code": ":page_facing_up:",
        "description": "Add or update license.",
        "name": "page-facing-up",
        "semver": "",
    },
    {
        "emoji": "💥",
        "entity": "&#x1f4a5;",
        "code": ":boom:",
        "description": "Introduce breaking changes.",
        "name": "boom",
        "semver": "major",
    },
    {
        "emoji": "🍱",
        "entity": "&#1F371",
        "code": ":bento:",
        "description": "Add or update assets.",
        "name": "bento",
        "semver": "patch",
    },
    {
        "emoji": "♿️",
        "entity": "&#9855;",
        "code": ":wheelchair:",
        "description": "Improve accessibility.",
        "name": "wheelchair",
        "semver": "patch",
    },
    {
        "emoji": "💡",
        "entity": "&#128161;",
        "code": ":bulb:",
        "description": "Add or update comments in source code.",
        "name": "bulb",
        "semver": "",
    },
    {
        "emoji": "🍻",
        "entity": "&#x1f37b;",
        "code": ":beers:",
        "description": "Write code drunkenly.",
        "name": "beers",
        "semver": "",
    },
    {
        "emoji": "💬",
        "entity": "&#128172;",
        "code": ":speech_balloon:",
        "description": "Add or update text and literals.",
        "name": "speech-balloon",
        "semver": "patch",
    },
    {
        "emoji": "🗃️",
        "entity": "&#128451;",
        "code": ":card_file_box:",
        "description": "Perform database related changes.",
        "name": "card-file-box",
        "semver": "patch",
    },
    {
        "emoji": "🔊",
        "entity": "&#128266;",
        "code": ":loud_sound:",
        "description": "Add or update logs.",
        "name": "loud-sound",
        "semver": "",
    },
    {
        "emoji": "🔇",
        "entity": "&#128263;",
        "code": ":mute:",
        "description": "Remove logs.",
        "name": "mute",
        "semver": "",
    },
    {
        "emoji": "👥",
        "entity": "&#128101;",
        "code": ":busts_in_silhouette:",
        "description": "Add or update contributor(s).",
        "name": "busts-in-silhouette",
        "semver": "",
    },
    {
        "emoji": "🚸",
        "entity": "&#128696;",
        "code": ":children_crossing:",
        "description": "Improve user experience / usability.",
        "name": "children-crossing",
        "semver": "patch",
    },
    {
        "emoji": "🏗️",
        "entity": "&#1f3d7;",
        "code": ":building_construction:",
        "description": "Make architectural changes.",
        "name": "building-construction",
        "semver": "",
    },
    {
        "emoji": "📱",
        "entity": "&#128241;",
        "code": ":iphone:",
        "description": "Work on responsive design.",
        "name": "iphone",
        "semver": "patch",
    },
    {
        "emoji": "🤡",
        "entity": "&#129313;",
        "code": ":clown_face:",
        "description": "Mock things.",
        "name": "clown-face",
        "semver": "",
    },
    {
        "emoji": "🥚",
        "entity": "&#129370;",
        "code": ":egg:",
        "description": "Add or update an easter egg.",
        "name": "egg",
        "semver": "patch",
    },
    {
        "emoji": "🙈",
        "entity": "&#8bdfe7;",
        "code": ":see_no_evil:",
        "description": "Add or update a .gitignore file.",
        "name": "see-no-evil",
        "semver": "",
    },
    {
        "emoji": "📸",
        "entity": "&#128248;",
        "code": ":camera_flash:",
        "description": "Add or update snapshots.",
        "name": "camera-flash",
        "semver": "",
    },
    {
        "emoji": "⚗️",
        "entity": "&#x2697;",
        "code": ":alembic:",
        "description": "Perform experiments.",
        "name": "alembic",
        "semver": "patch",
    },
    {
        "emoji": "🔍️",
        "entity": "&#128269;",
        "code": ":mag:",
        "description": "Improve SEO.",
        "name": "mag",
        "semver": "patch",
    },
    {
        "emoji": "🏷️",
        "entity": "&#127991;",
        "code": ":label:",
        "description": "Add or update types.",
        "name": "label",
        "semver": "patch",
    },
    {
        "emoji": "🌱",
        "entity": "&#127793;",
        "code": ":seedling:",
        "description": "Add or update seed files.",
        "name": "seedling",
        "semver": "",
    },
    {
        "emoji": "🚩",
        "entity": "&#x1F6A9;",
        "code": ":triangular_flag_on_post:",
        "description": "Add, update, or remove feature flags.",
        "name": "triangular-flag-on-post",
        "semver": "patch",
    },
    {
        "emoji": "🥅",
        "entity": "&#x1F945;",
        "code": ":goal_net:",
        "description": "Catch errors.",
        "name": "goal-net",
        "semver": "patch",
    },
    {
        "emoji": "💫",
        "entity": "&#x1f4ab;",
        "code": ":dizzy:",
        "description": "Add or update animations and transitions.",
        "name": "animation",
        "semver": "patch",
    },
    {
        "emoji": "🗑️",
        "entity": "&#x1F5D1;",
        "code": ":wastebasket:",
        "description": "Deprecate code that needs to be cleaned up.",
        "name": "wastebasket",
        "semver": "patch",
    },
    {
        "emoji": "🛂",
        "entity": "&#x1F6C2;",
        "code": ":passport_control:",
        "description": "Work on code related to authorization, roles and permissions.",
        "name": "passport-control",
        "semver": "patch",
    },
    {
        "emoji": "🩹",
        "entity": "&#x1FA79;",
        "code": ":adhesive_bandage:",
        "description": "Simple fix for a non-critical issue.",
        "name": "adhesive-bandage",
        "semver": "patch",
    },
    {
        "emoji": "🧐",
        "entity": "&#x1F9D0;",
        "code": ":monocle_face:",
        "description": "Data exploration/inspection.",
        "name": "monocle-face",
        "semver": "",
    },
    {
        "emoji": "⚰️",
        "entity": "&#x26B0;",
        "code": ":coffin:",
        "description": "Remove dead code.",
        "name": "coffin",
        "semver": "",
    },
    {
        "emoji": "🧪",
        "entity": "&#x1F9EA;",
        "code": ":test_tube:",
        "description": "Add a failing test.",
        "name": "test-tube",
        "semver": "",
    },
    {
        "emoji": "👔",
        "entity": "&#128084;",
        "code": ":necktie:",
        "description": "Add or update business logic.",
        "name": "necktie",
        "semver": "patch",
    },
    {
        "emoji": "🩺",
        "entity": "&#x1FA7A;",
        "code": ":stethoscope:",
        "description": "Add or update healthcheck.",
        "name": "stethoscope",
        "semver": "",
    },
    {
        "emoji": "🧱",
        "entity": "&#x1f9f1;",
        "code": ":bricks:",
        "description": "Infrastructure related changes.",
        "name": "bricks",
        "semver": "",
    },
    {
        "emoji": "🧑‍💻",
        "entity": "&#129489;&#8205;&#128187;",
        "code": ":technologist:",
        "description": "Improve developer experience.",
        "name": "technologist",
        "semver": "",
    },
    {
        "emoji": "💸",
        "entity": "&#x1F4B8;",
        "code": ":money_with_wings:",
        "description": "Add sponsorships or money related infrastructure.",
        "name": "money-with-wings",
        "semver": "",
    },
    {
        "emoji": "🧵",
        "entity": "&#x1F9F5;",
        "code": ":thread:",
        "description": "Add or update code related to multithreading or concurrency.",
        "name": "thread",
        "semver": "",
    },
    {
        "emoji": "🦺",
        "entity": "&#x1F9BA;",
        "code": ":safety_vest:",
        "description": "Add or update code related to validation.",
        "name": "safety-vest",
        "semver": "",
    },
]
"""
List of emojis and their code and description according
to https://gitmoji.dev/
"""
