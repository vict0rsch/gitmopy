import json
from datetime import datetime
from typing import Dict, List, Optional

from rich import print

from gitmopy.utils import HISTORY_PATH, GITMOJIS, load_config

HISTORY = []


def load_history() -> List[Dict[str, str]]:
    """
    Load history from ``${HISTORY_PATH}`` file.

    Returns an empty list if the file does not exist.
    """
    global HISTORY
    history = []
    _history = [
        {
            "timestamp": 2686784403,
            "emoji": "🧵",
            "scope": "all",
            "title": "Heallo",
            "message": "meessaage",
        },
        {
            "timestamp": 1686784120,
            "emoji": "🧵",
            "scope": "all ea raz",
            "title": "Heallo",
            "message": "meessaage",
        },
        {
            "timestamp": 1686783103,
            "emoji": "💸",
            "scope": "all ea ezar",
            "title": "Heallo",
            "message": "meessaage",
        },
        {
            "timestamp": 1686784403,
            "emoji": "💸",
            "scope": "erzar",
            "title": "Heallo",
            "message": "meessaage",
        },
        {
            "timestamp": 1686784403,
            "emoji": "🧵",
            "scope": "feza",
            "title": "Heallo",
            "message": "meessaage",
        },
    ]
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text())

    HISTORY = history


def timestamp() -> int:
    """
    Get the current local timestamp as an int.

    Returns:
        int: Current timestamp.
    """
    return int(datetime.now().timestamp())


def save_to_history(
    commit_dict: Dict[str, str], history: Optional[List[Dict[str, str]]] = None
) -> None:
    """
    Writes a commit dictionnary to the history file in ``${HISTORY_PATH}``.

    Args:
        commit_dict (dict): The commit details to write to the history file.
            Keys must be "emoji", "scope", "title" and "message". A "timestamp"
            key will be added automatically.
        history (list, optional): History to append to. Will use the global one if
            ``None``. Defaults to ``None``.
    """
    if history is None:
        history = HISTORY
    history.append(
        {
            **commit_dict,
            "timestamp": timestamp(),
        }
    )
    if not HISTORY_PATH.parent.exists():
        HISTORY_PATH.parent.mkdir(parents=True)
        print("[bold green]Created history file in", str(HISTORY_PATH), end="\n\n")

    HISTORY_PATH.write_text(json.dumps(history))


def sort_emojis(
    gitmojis: List[Dict[str, str]], history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, str]]:
    """
    Sort emojis by most recent usage in history.

    Args:
        gitmojis (list): All gitmojis available as a list of dicts.
        history (list, optional): History to sort from. Will use the global one if
            ``None``. Defaults to ``None``.

    Returns:
        List[Dict[str, str]]: Sorted gitmojis.
    """
    if history is None:
        history = HISTORY
    dater = {}
    for commit in history:
        dater[commit["emoji"]] = commit["timestamp"]
    gitmojis = sorted(gitmojis, key=lambda x: dater.get(x["emoji"], 0), reverse=True)
    return gitmojis


def gitmojis_setup() -> None:
    """
    Setup the emoji list.
    Adds a "name" and "value" key to each emoji.
    """
    global GITMOJIS

    config = load_config()

    if not config["enable_history"]:
        return

    for e in GITMOJIS:
        e["name"] = e["emoji"] + " " + e["description"]
        e["value"] = e["emoji"]
    load_history()
    GITMOJIS = sort_emojis(GITMOJIS)
