import fuzzysearch
from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from prompt_toolkit.completion import Completer, Completion

from gitmopy import history as gmp_history
from gitmopy.utils import load_config, save_config, DEFAULT_CHOICES, APP_PATH, GITMOJIS


def emo_setup():
    global GITMOJIS

    for e in GITMOJIS:
        e["match_str"] = "".join(e.values())
        e["name"] = e["emoji"] + " " + e["description"]
        e["value"] = e["emoji"]
        e["count"] = 0
    gmp_history.load_history()
    GITMOJIS = gmp_history.sort_emojis(GITMOJIS)


def match_emojis(match, fuzzy=False):
    global GITMOJIS

    return [
        e
        for e in GITMOJIS
        if fuzzysearch.find_near_matches(match, e["match_str"], max_l_dist=int(fuzzy))
    ]


class GMPCompleter(Completer):
    def __init__(self, key):
        self.key = key
        self.candidates = {}
        for c in gmp_history.HISTORY:
            if c[key] not in self.candidates:
                self.candidates[c[key]] = c["timestamp"]
            else:
                self.candidates[c[key]] = max(self.candidates[c[key]], c["timestamp"])
        super().__init__()

    def get_completions(self, document, complete_event):
        matched = sorted(
            [
                (k, v)
                for k, v in self.candidates.items()
                if k.lower().startswith(document.text.lower())
            ],
            key=lambda x: x[1],
            reverse=True,
        )
        for m in matched[:10]:
            yield Completion(m[0], start_position=-len(document.text))


def commit_prompt(config):
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
    if config["capitalize_title"]:
        title = title.capitalize()

    if not config["skip_message"]:
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

    return {
        "emoji": emoji,
        "scope": scope,
        "title": title,
        "message": message,
    }


def setup_prompt():
    config = load_config()

    choices = [
        Choice(c["value"], c["name"], config.get(c["value"], c["default"]))
        for c in DEFAULT_CHOICES
    ]

    selected = inquirer.checkbox(
        message="Setup gitmopy locally.",
        instruction="Use 'space' to (de-)select.",
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


def git_add_prompt(status):
    choices = []
    for s in status["unstaged"]:
        choices.append(Choice(s, f"{s} -- unstaged", True))
    if len(choices) > 0:
        choices.append(Separator())
    for s in status["untracked"]:
        choices.append(Choice(s, f"{s} -- untracked", True))

    selected = inquirer.checkbox(
        message="Select files to add for the commit.",
        choices=choices,
        cycle=True,
        transformer=lambda result: "",
        qmark="❓",
        amark="✓",
    ).execute()

    return selected


emo_setup()
