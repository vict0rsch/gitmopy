import json
from gitmopy.utils import APP_PATH
from datetime import datetime
from rich import print


HISTORY_PATH = APP_PATH / "history.json"
HISTORY = []


def load_history():
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
    return int(datetime.now().timestamp())


def save_to_history(commit_dict, history=None):
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


def sort_emojis(emodata, history=None):
    """Sort emojis by usage in history"""
    if history is None:
        history = HISTORY
    dater = {}
    for commit in history:
        dater[commit["emoji"]] = commit["timestamp"]
    emodata["gitmojis"] = sorted(
        emodata["gitmojis"], key=lambda x: dater.get(x["emoji"], 0), reverse=True
    )
    return emodata
