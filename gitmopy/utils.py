from os.path import expandvars
from pathlib import Path
from typing import Union
from yaml import safe_load, safe_dump
from rich import print
import typer


def resolve_path(path: Union[str, Path]) -> Path:
    return Path(expandvars(path)).expanduser().resolve()


APP_PATH = resolve_path(typer.get_app_dir("gitmopy"))

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
        "name": "Remember commit history for auto-complete and emoji sorting"
        + f" (saved in {str(APP_PATH)}/history.json)",
        "default": True,
    },
]
DEFAULT_CONFIG = {c["value"]: c["default"] for c in DEFAULT_CHOICES}


def load_config():
    yaml_path = APP_PATH / "config.yaml"
    if yaml_path.exists():
        return {**DEFAULT_CONFIG, **safe_load(yaml_path.read_text())}
    return DEFAULT_CONFIG


def save_config(config):
    yaml_path = APP_PATH / "config.yaml"
    if not yaml_path.exists():
        print("[bold yellow] Creating config file [/bold yellow]", str(yaml_path))
    yaml_path.parent.mkdir(exist_ok=True)
    yaml_path.write_text(safe_dump(config))
    print("✅ Config updated")


def print_staged_files(staged):
    nst = len(staged)
    s = "" if nst == 1 else "s"
    print(f"[green3]Currently {nst} staged file{s} for commit:[/green3]")
    for f in staged:
        print(f"  [grey66]- {f}[/grey66]")
