"""
Constants for gitmopy.
"""

from os.path import expandvars
from pathlib import Path

import typer
from yaml import safe_load

APP_PATH = (
    Path(expandvars(typer.get_app_dir("gitmopy", force_posix=True)))
    .expanduser()
    .resolve()
)
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

USER_EMOJIS_PATH = APP_PATH / "custom_gitmojis.yaml"
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
    "a": "gray",
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
    {
        "value": "emoji_set",
        "name": "Emoji set to use for commits",
        "default": "gitmoji",
        "options": ["gitmoji", "ai-devmojis"],
    },
    {
        "value": "default_commit_flags",
        "name": "Default commit binary flags used in `gitmopy start`",
        "default": [],
        "options": [],  # must be set programmatically by `set_start_options`
    },
    {
        "value": "default_commit_args",
        "name": "Default commit arguments used in `gitmopy start`",
        "default": {"repo": ".", "remote": "origin"},
        "options": {
            "repo": "Path to the git repository",
            "remote": "Comma-separated list of remotes to push to",
        },
    },
]
"""
Choices for the setup prompt.
"""


DEFAULT_CONFIG = {c["value"]: c["default"] for c in DEFAULT_CHOICES}
"""
Default gitmopy configuration.
"""

HISTORY = []
"""
User's commit history. Will be loaded from ``${APP_PATH}/history.json``.

Empty by default or if user diabled it.
"""

EMOJIS = []
"""
The loaded emojis. Will be set to :py:const:`gitmopy.GITMOJIS` or
:py:const:`gitmopy.AI_DEVMOJIS` depending on the user's choice, and updated with the
user's custom emoji set.
"""

# https://github.com/carloscuesta/gitmoji/blob/master/packages/gitmojis/src/gitmojis.json
GITMOJIS = safe_load((Path(__file__).parent / "assets/gitmojis.yaml").read_text())
"""
List of emojis and their code and description according
to https://gitmoji.dev/
"""

AI_DEVMOJIS = safe_load((Path(__file__).parent / "assets/ai_devmojis.yaml").read_text())
"""
List of emojis and their code and description according to a custom specification
tailored for AI/ML projects and development.
"""

CONVENTIONAL = safe_load(
    (Path(__file__).parent / "assets/conventional.yaml").read_text()
)
"""
List of conventional commits and their code and description.
"""
