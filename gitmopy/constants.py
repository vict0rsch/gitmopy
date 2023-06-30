"""
Constants for gitmopy.
"""
from os.path import expandvars
from pathlib import Path

import typer

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

HISTORY = []
"""
User's commit history. Will be loaded from ``${APP_PATH}/history.json``.

Empty by default or if user diabled it.
"""

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
