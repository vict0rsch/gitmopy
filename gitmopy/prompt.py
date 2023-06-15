from typing import Any, Dict, List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from gitmopy import history as gmp_history
from gitmopy.utils import APP_PATH, DEFAULT_CHOICES, GITMOJIS, load_config, save_config


class GMPCompleter(Completer):
    def __init__(self, key: str, max_results: Optional[int] = 10):
        """
        A completer that completes a text prompt from the user's history.
        Completions are sorted by most recent first.
        Returns up to ``self.max_results`` results.

        Args:
            key (str): Key to complete from. Must be one of "scope", "title", "message".
        """
        self.key = key
        self.max_results = max_results
        self.candidates = {}
        for c in gmp_history.HISTORY:
            if c[key] not in self.candidates:
                self.candidates[c[key]] = c["timestamp"]
            else:
                self.candidates[c[key]] = max(self.candidates[c[key]], c["timestamp"])
        super().__init__()

    def get_completions(self, document: Document, complete_event: Any) -> Completion:
        """
        Get completions for the current prompt.

        A completion is a string from the user's history that starts with all
        the characters in the current prompt.

        Case insensitive.

        Args:
            document (prompt_toolkit.document.Document): The current document from the
                prompt.
            complete_event (Any): Unused.

        Yields:
            Completion: A completion object that replaces the current user's input.
        """
        matched = sorted(
            [
                (k, v)
                for k, v in self.candidates.items()
                if k.lower().startswith(document.text.lower())
            ],
            key=lambda x: x[1],
            reverse=True,
        )
        for m in matched[: self.max_results]:
            yield Completion(m[0], start_position=-len(document.text))


def commit_prompt(config: Dict[str, bool]) -> Dict[str, str]:
    """
    Prompt the user for a commit message in up to 4 steps:
    - Select gitmoji
    - Select scope
    - Enter title
    - Enter message

    Scope and message are optional.
    Scope and message can be bypassed from the config (run ``gitmopy config``)
    Scope, title and message are completed from the user's history if
        ``config["enable_history"]`` is ``True``.

    Args:
        config (dict): Configuration dictionary, from ``gitmopy config``.

    Returns:
        dict: User-specified commit as a dict with keys
            ``"emoji"``, ``"scope"``, ``"title"``, ``"message"``.
    """

    # get the commit's gitmoji
    emoji = (
        inquirer.fuzzy(
            message="Select gitmoji:",
            choices=GITMOJIS,
            multiselect=False,
            max_height="70%",
            mandatory=True,
            qmark="❓",
            amark="✓",
        )
        .execute()
        .strip()
    )

    scope = message = ""

    if not config["skip_scope"]:
        # get the commit's scope
        scope = (
            inquirer.text(
                message="Select scope (optional):",
                mandatory=False,
                qmark="⭕️",
                amark="✓",
                completer=GMPCompleter("scope"),
            )
            .execute()
            .strip()
        )

    # get the commit's title
    title = (
        inquirer.text(
            message="Commit title:",
            long_instruction="<= 50 characters ideally",
            mandatory=True,
            mandatory_message="You must provide a commit tile",
            validate=lambda t: len(t) > 0,
            invalid_message="You must provide a commit tile",
            qmark="⭐️",
            amark="✓",
            transformer=lambda t: t.capitalize() if config["capitalize_title"] else t,
            completer=GMPCompleter("title"),
        )
        .execute()
        .strip()
    )
    # Capitalize the title if the user wants to (from config)
    if config["capitalize_title"]:
        title = title.capitalize()

    if not config["skip_message"]:
        # get the commit's message
        message = (
            inquirer.text(
                message="Commit details (optional):",
                mandatory=False,
                qmark="💬",
                amark="✓",
                completer=GMPCompleter("message"),
            )
            .execute()
            .strip()
        )

    # return commit details as a dict
    return {
        "emoji": emoji,
        "scope": scope,
        "title": title,
        "message": message,
    }


def config_prompt() -> None:
    """
    Prompt the user for configuration options.
    Will setup:
    - Whether to skip scope
    - Whether to skip message
    - Whether to capitalize title
    - Whether to enable history

    Will save the configuration in ``${APP_PATH}/config.yaml``.
    """
    config = load_config()

    choices = [
        Choice(c["value"], c["name"], config.get(c["value"], c["default"]))
        for c in DEFAULT_CHOICES
    ]

    selected = inquirer.checkbox(
        message="Configure gitmopy locally.",
        instruction="Use 'space' to (de-)select, 'enter' to validate.",
        long_instruction=f"Config will be saved in {str(APP_PATH)}/config.yaml.",
        choices=choices,
        cycle=True,
        transformer=lambda result: "",
        qmark="❓",
        amark="✓",
    ).execute()

    selected = set(selected)

    for c in choices:
        config[c.value] = c.value in selected

    save_config(config)


def git_add_prompt(status: Dict[str, List[str]]) -> List[str]:
    """
    Start a prompt to select files to add to the commit.

    Files are grouped by status (unstaged, untracked).

    Files are all selected by default.

    Args:
        status (dict): Dictionary of files grouped by status.

    Returns:
        list: List of all the files selected by the user.
    """
    choices = []
    for s in status["unstaged"]:
        choices.append(Choice(s, f"{s} -- unstaged", True))
    if len(choices) > 0:
        choices.append(Separator())
    for s in status["untracked"]:
        choices.append(Choice(s, f"{s} -- untracked", True))

    selected = inquirer.checkbox(
        message="Select files to add for the commit.",
        instruction="Use 'space' to (de-)select, 'enter' to validate.",
        choices=choices,
        cycle=True,
        transformer=lambda result: "",
        qmark="❓",
        amark="✓",
    ).execute()

    return selected


def choose_remote_prompt(remotes: List[str]) -> List[str]:
    choices = [Choice(r.name, r.name, True) for r in remotes]
    selected = inquirer.checkbox(
        "Select remotes to push to:",
        instruction="Use 'space' to (de-)select, 'enter' to validate.",
        choices=choices,
        cycle=True,
        qmark="❓",
        amark="✓",
        transformer=lambda result: "Pushing to " + ", ".join(result),
    ).execute()

    return selected
