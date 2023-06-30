"""
User history management.

In particular:
* sort emojis by timestamp
* prepare history for prompt completion (title, scope, message)
"""
import json
from datetime import datetime
from typing import Dict, List

import gitmopy.constants as gpyc
from gitmopy.utils import col, load_config, load_user_gitmojis, print


def load_history() -> List[Dict[str, str]]:
    """
    Load history from ``${HISTORY_PATH}`` file.

    Returns an empty list if the file does not exist.
    """
    history = []

    if gpyc.HISTORY_PATH.exists():
        try:
            history = json.loads(gpyc.HISTORY_PATH.read_text())
        except Exception as e:
            print(
                col(f"Error loading history from {str(gpyc.HISTORY_PATH)}", "red", True)
            )
            print(e)
            history = []

    gpyc.HISTORY = history


def timestamp() -> int:
    """
    Get the current local timestamp as an int.

    Returns:
        int: Current timestamp.
    """
    return int(datetime.now().timestamp())


def save_to_history(commit_dict: Dict[str, str]) -> None:
    """
    Writes a commit dictionnary to the history file in ``${HISTORY_PATH}``.

    Args:
        commit_dict (dict): The commit details to write to the history file.
            Keys must be "emoji", "scope", "title" and "message". A "timestamp"
            key will be added automatically.
        history (list, optional): History to append to. Will use the global one if
            ``None``. Defaults to ``None``.
    """
    gpyc.HISTORY.append(
        {
            **commit_dict,
            "timestamp": timestamp(),
        }
    )
    if not gpyc.HISTORY_PATH.parent.exists():
        gpyc.HISTORY_PATH.parent.mkdir(parents=True)
    if not gpyc.HISTORY_PATH.exists():
        print("[bold green]Created history file in", str(gpyc.HISTORY_PATH), end="\n\n")

    gpyc.HISTORY_PATH.write_text(json.dumps(gpyc.HISTORY))


def sort_emojis() -> List[Dict[str, str]]:
    """
    Sort emojis by most recent usage in history.

    Args:
        gitmojis (list): All gitmojis available as a list of dicts.
        history (list, optional): History to sort from. Will use the global one if
            ``None``. Defaults to ``None``.

    Returns:
        List[Dict[str, str]]: Sorted gitmojis.
    """
    dater = {}
    for commit in gpyc.HISTORY:
        dater[commit["emoji"]] = commit["timestamp"]
    gpyc.GITMOJIS.sort(key=lambda x: dater.get(x["emoji"], 0), reverse=True)


def gitmojis_setup() -> None:
    """
    Setup the emoji list.

    * loads the config
    * adds ``name`` and ``value`` keys to each emoji (for prompt Choices)
    * loads the history (if enabled)
    * sorts the emojis by most recent usage in history (if enabled)
    """
    config = load_config()
    emo_dict = {e["emoji"]: e for e in gpyc.GITMOJIS}
    user_emojis = load_user_gitmojis()
    for u in user_emojis:
        emo_dict[u["emoji"]] = u

    gpyc.GITMOJIS = list(emo_dict.values())

    for k, e in enumerate(gpyc.GITMOJIS):
        gpyc.GITMOJIS[k]["name"] = e["emoji"] + " " + e["description"]
        gpyc.GITMOJIS[k]["value"] = e["emoji"]

    if not config["enable_history"]:
        return

    load_history()
    sort_emojis()
