"""
User history management.

In particular:
* sort emojis by timestamp
* prepare history for prompt completion (title, scope, message)
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from gitmopy.utils import GITMOJIS, HISTORY_PATH, load_config, print

HISTORY = []


def load_history() -> List[Dict[str, str]]:
    """
    Load history from ``${HISTORY_PATH}`` file.

    Returns an empty list if the file does not exist.
    """
    global HISTORY
    history = []

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
    gitmojis.sort(key=lambda x: dater.get(x["emoji"], 0), reverse=True)


def gitmojis_setup() -> None:
    """
    Setup the emoji list.

    * loads the config
    * adds ``name`` and ``value`` keys to each emoji (for prompt Choices)
    * loads the history (if enabled)
    * sorts the emojis by most recent usage in history (if enabled)
    """
    global GITMOJIS

    config = load_config()

    for k, e in enumerate(GITMOJIS):
        GITMOJIS[k]["name"] = e["emoji"] + " " + e["description"]
        GITMOJIS[k]["value"] = e["emoji"]

    if not config["enable_history"]:
        return

    load_history()
    sort_emojis(GITMOJIS)
