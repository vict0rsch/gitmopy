"""
Module handling user prompts.

Prompts typically parameterize the commit message or ``gitmopy``'s behavior.
"""

from typing import Any, Callable, Dict, List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

import gitmopy.constants as gpyc
from gitmopy.constants import _sentinels
from gitmopy.utils import (
    choice_separator,
    clear_line_and_move_up,
    load_config,
    safe_capitalize,
    save_config,
)


class GMPCompleter(Completer):
    def __init__(self, key: str, max_results: Optional[int] = 10):
        """
        A completer that completes a text prompt from the user's history.

        Completions are sorted by most recent first.
        Returns up to ``self.max_results`` results.

        Args:
            key (str): Key to complete from. Must be one of "scope", "title", "message".
            max_results (int): Maximum number of results to return. Defaults to 10.
        """
        self.key = key
        self.max_results = max_results
        self.candidates = {}
        for c in gpyc.HISTORY:
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


def try_func_with_keyboard_interrupt(func: Callable, *args, **kwargs):
    """
    Try a function and catch a KeyboardInterrupt.
    """
    try:
        return func(*args, **kwargs)
    except KeyboardInterrupt:
        return None


def commit_prompt(
    config: Dict[str, bool],
    state: Dict[str, str] | None = None,
    simple: bool = False,
) -> Dict[str, str]:
    """
    Prompt the user for emoji, scope title and message to make a commit message.

    Scope and message are optional.
    Scope and message can be bypassed from the config (run ``gitmopy config``)
    Scope, title and message are completed from the user's history if
        ``config["enable_history"]`` is ``True``.

    Args:
        config (dict): Configuration dictionary, from ``gitmopy config``.
        state (dict): State dictionary from previous prompts.
    Returns:
        dict: User-specified commit as a dict with keys
            ``"emoji"``, ``"scope"``, ``"title"``, ``"message"``.
    """
    # get the commit's gitmoji
    emoji = state.get("emoji")
    if emoji is None:
        emoji_message = "Select gitmoji:" if not simple else "Select Conventional type:"
        emoji_choices = gpyc.EMOJIS if not simple else gpyc.CONVENTIONAL
        emoji = try_func_with_keyboard_interrupt(
            lambda: inquirer.fuzzy(
                message=emoji_message,
                choices=emoji_choices,
                multiselect=False,
                max_height="70%",
                mandatory=True,
                qmark="❓",
                amark="✓",
            )
            .execute()
            .strip()
        )
    if emoji is None:
        return _sentinels["cancelled"]
    state["emoji"] = emoji

    scope = message = ""

    if not config["skip_scope"] and not simple:
        # get the commit's scope
        scope = state.get("scope")
        if scope is None:
            scope = try_func_with_keyboard_interrupt(
                lambda: inquirer.text(
                    message="Select scope (optional):",
                    mandatory=False,
                    qmark="⭕️",
                    amark="✓",
                    completer=GMPCompleter("scope"),
                )
                .execute()
                .strip()
            )
        if scope is None:
            state.pop("emoji")
            clear_line_and_move_up()
            return commit_prompt(config, state, simple)
    state["scope"] = scope

    # get the commit's title
    title = state.get("title")
    if title is None:
        title = try_func_with_keyboard_interrupt(
            lambda: inquirer.text(
                message="Commit title:",
                long_instruction="<= 50 characters ideally",
                mandatory=True,
                mandatory_message="You must provide a commit tile",
                validate=lambda t: len(t) > 0,
                invalid_message="You must provide a commit tile",
                qmark="⭐️",
                amark="✓",
                transformer=lambda t: safe_capitalize(t)
                if config["capitalize_title"]
                else t,
                completer=GMPCompleter("title"),
            )
            .execute()
            .strip()
        )
    if title is None:
        state.pop("scope")
        if simple:
            state.pop("emoji")
        clear_line_and_move_up()
        return commit_prompt(config, state, simple)
    state["title"] = title

    # Capitalize the title if the user wants to (from config)
    if config["capitalize_title"]:
        title = safe_capitalize(title)

    if not config["skip_message"]:
        # get the commit's message
        message = state.get("message")
        if message is None:
            message = try_func_with_keyboard_interrupt(
                lambda: inquirer.text(
                    message="Commit details (optional):",
                    mandatory=False,
                    qmark="💬",
                    amark="✓",
                    completer=GMPCompleter("message"),
                )
                .execute()
                .strip()
            )
        if message is None:
            state.pop("title")
            clear_line_and_move_up()
            return commit_prompt(config, state, simple)
    state["message"] = message

    # return commit details as a dict
    return state


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
        for c in gpyc.DEFAULT_CHOICES
        if isinstance(c["default"], bool)
    ]

    selected = inquirer.checkbox(
        message="Configure gitmopy locally.",
        instruction="Use 'space' to (de-)select, 'enter' to validate.",
        long_instruction=f"Config will be saved in {str(gpyc.APP_PATH)}/config.yaml.",
        choices=choices,
        cycle=True,
        transformer=lambda result: "",
        qmark="❓",
        amark="✓",
    ).execute()

    selected = set(selected)

    lists = [
        c
        for c in gpyc.DEFAULT_CHOICES
        if isinstance(c["default"], str) and "options" in c
    ]
    options = {}

    for ldict in lists:
        option = inquirer.select(
            message=ldict["name"],
            choices=ldict["options"],
            default=ldict["default"],
            qmark="❓",
            amark="✓",
        ).execute()
        options[ldict["value"]] = option

    multiple_choices = [
        c
        for c in gpyc.DEFAULT_CHOICES
        if isinstance(c["default"], list) and "options" in c
    ]

    for c in multiple_choices:
        option = inquirer.checkbox(
            message=c["name"],
            choices=c["options"],
            default=c["default"],
            qmark="❓",
            amark="✓",
        ).execute()
        options[c["value"]] = option

    string_inputs = [c for c in gpyc.DEFAULT_CHOICES if isinstance(c["default"], dict)]

    for c in string_inputs:
        for k, v in c["options"].items():
            option = inquirer.text(
                message=f"{k} ({v}):",
                qmark="❓",
                amark="✓",
                default=c["default"][k],
            ).execute()
            if c["value"] not in options:
                options[c["value"]] = {}
            options[c["value"]][k] = option

    for c in choices:
        config[c.value] = c.value in selected
    config.update(options)

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
    if len(status["unstaged"]) > 0:
        choices.append(choice_separator("Unstaged files"))
    for s in status["unstaged"]:
        choices.append(Choice(s, s, True))

    if len(status["untracked"]) > 0:
        choices.append(choice_separator("Untracked files"))
    for s in status["untracked"]:
        choices.append(Choice(s, s, True))

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
    """
    Prompt the user to select remotes to push to.

    Args:
        remotes (List[str]): Available remotes.

    Returns:
        List[str]: Selected remotes.
    """
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


def set_upstream_prompt(branch_name: str, remote_name: str) -> bool:
    """
    Prompt the user to set the upstream branch for a remote.

    Args:
        branch_name (str): Branch name to set on the remote.
        remote_name (str): Remote name.

    Returns:
        bool: Whether or not to set the upstream branch.
    """
    return inquirer.confirm(
        f"'{remote_name}' does not have a branch named '{branch_name}'."
        + " Create upstream branch?",
        qmark="❓",
        amark="✓",
        default=True,
    ).execute()


def what_now_prompt(choices: Dict[str, str]) -> str:
    """
    Prompt the user to select what to do next.

    Choices must be a dictlike `{value: name}`.

    Args:
        choices (Dict[str, str]): Available choices.

    Returns:
        str: User's choice.
    """
    choices = [Choice(k, v, True) for k, v in choices.items()]
    return inquirer.select(
        message="What do you want to do now?",
        choices=choices,
        qmark="❓",
        amark="✓",
        default=choices[0],
        cycle=True,
    ).execute()
