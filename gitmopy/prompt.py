import fuzzysearch
from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from prompt_toolkit.completion import Completer, Completion

from gitmopy import history as gmp_history
from gitmopy.utils import load_config, save_config, DEFAULT_CHOICES, APP_PATH

# https://github.com/carloscuesta/gitmoji/blob/master/packages/gitmojis/src/gitmojis.json
EMODATA = {
    "$schema": "https://gitmoji.dev/api/gitmojis/schema",
    "gitmojis": [
        {
            "emoji": "🎨",
            "entity": "&#x1f3a8;",
            "code": ":art:",
            "description": "Improve structure / format of the code.",
            "name": "art",
            "semver": "",
        },
        {
            "emoji": "⚡️",
            "entity": "&#x26a1;",
            "code": ":zap:",
            "description": "Improve performance.",
            "name": "zap",
            "semver": "patch",
        },
        {
            "emoji": "🔥",
            "entity": "&#x1f525;",
            "code": ":fire:",
            "description": "Remove code or files.",
            "name": "fire",
            "semver": "",
        },
        {
            "emoji": "🐛",
            "entity": "&#x1f41b;",
            "code": ":bug:",
            "description": "Fix a bug.",
            "name": "bug",
            "semver": "patch",
        },
        {
            "emoji": "🚑️",
            "entity": "&#128657;",
            "code": ":ambulance:",
            "description": "Critical hotfix.",
            "name": "ambulance",
            "semver": "patch",
        },
        {
            "emoji": "✨",
            "entity": "&#x2728;",
            "code": ":sparkles:",
            "description": "Introduce new features.",
            "name": "sparkles",
            "semver": "minor",
        },
        {
            "emoji": "📝",
            "entity": "&#x1f4dd;",
            "code": ":memo:",
            "description": "Add or update documentation.",
            "name": "memo",
            "semver": "",
        },
        {
            "emoji": "🚀",
            "entity": "&#x1f680;",
            "code": ":rocket:",
            "description": "Deploy stuff.",
            "name": "rocket",
            "semver": "",
        },
        {
            "emoji": "💄",
            "entity": "&#ff99cc;",
            "code": ":lipstick:",
            "description": "Add or update the UI and style files.",
            "name": "lipstick",
            "semver": "patch",
        },
        {
            "emoji": "🎉",
            "entity": "&#127881;",
            "code": ":tada:",
            "description": "Begin a project.",
            "name": "tada",
            "semver": "",
        },
        {
            "emoji": "✅",
            "entity": "&#x2705;",
            "code": ":white_check_mark:",
            "description": "Add, update, or pass tests.",
            "name": "white-check-mark",
            "semver": "",
        },
        {
            "emoji": "🔒️",
            "entity": "&#x1f512;",
            "code": ":lock:",
            "description": "Fix security issues.",
            "name": "lock",
            "semver": "patch",
        },
        {
            "emoji": "🔐",
            "entity": "&#x1f510;",
            "code": ":closed_lock_with_key:",
            "description": "Add or update secrets.",
            "name": "closed-lock-with-key",
            "semver": "",
        },
        {
            "emoji": "🔖",
            "entity": "&#x1f516;",
            "code": ":bookmark:",
            "description": "Release / Version tags.",
            "name": "bookmark",
            "semver": "",
        },
        {
            "emoji": "🚨",
            "entity": "&#x1f6a8;",
            "code": ":rotating_light:",
            "description": "Fix compiler / linter warnings.",
            "name": "rotating-light",
            "semver": "",
        },
        {
            "emoji": "🚧",
            "entity": "&#x1f6a7;",
            "code": ":construction:",
            "description": "Work in progress.",
            "name": "construction",
            "semver": "",
        },
        {
            "emoji": "💚",
            "entity": "&#x1f49a;",
            "code": ":green_heart:",
            "description": "Fix CI Build.",
            "name": "green-heart",
            "semver": "",
        },
        {
            "emoji": "⬇️",
            "entity": "⬇️",
            "code": ":arrow_down:",
            "description": "Downgrade dependencies.",
            "name": "arrow-down",
            "semver": "patch",
        },
        {
            "emoji": "⬆️",
            "entity": "⬆️",
            "code": ":arrow_up:",
            "description": "Upgrade dependencies.",
            "name": "arrow-up",
            "semver": "patch",
        },
        {
            "emoji": "📌",
            "entity": "&#x1F4CC;",
            "code": ":pushpin:",
            "description": "Pin dependencies to specific versions.",
            "name": "pushpin",
            "semver": "patch",
        },
        {
            "emoji": "👷",
            "entity": "&#x1f477;",
            "code": ":construction_worker:",
            "description": "Add or update CI build system.",
            "name": "construction-worker",
            "semver": "",
        },
        {
            "emoji": "📈",
            "entity": "&#x1F4C8;",
            "code": ":chart_with_upwards_trend:",
            "description": "Add or update analytics or track code.",
            "name": "chart-with-upwards-trend",
            "semver": "patch",
        },
        {
            "emoji": "♻️",
            "entity": "&#x267b;",
            "code": ":recycle:",
            "description": "Refactor code.",
            "name": "recycle",
            "semver": "",
        },
        {
            "emoji": "➕",
            "entity": "&#10133;",
            "code": ":heavy_plus_sign:",
            "description": "Add a dependency.",
            "name": "heavy-plus-sign",
            "semver": "patch",
        },
        {
            "emoji": "➖",
            "entity": "&#10134;",
            "code": ":heavy_minus_sign:",
            "description": "Remove a dependency.",
            "name": "heavy-minus-sign",
            "semver": "patch",
        },
        {
            "emoji": "🔧",
            "entity": "&#x1f527;",
            "code": ":wrench:",
            "description": "Add or update configuration files.",
            "name": "wrench",
            "semver": "patch",
        },
        {
            "emoji": "🔨",
            "entity": "&#128296;",
            "code": ":hammer:",
            "description": "Add or update development scripts.",
            "name": "hammer",
            "semver": "",
        },
        {
            "emoji": "🌐",
            "entity": "&#127760;",
            "code": ":globe_with_meridians:",
            "description": "Internationalization and localization.",
            "name": "globe-with-meridians",
            "semver": "patch",
        },
        {
            "emoji": "✏️",
            "entity": "&#59161;",
            "code": ":pencil2:",
            "description": "Fix typos.",
            "name": "pencil2",
            "semver": "patch",
        },
        {
            "emoji": "💩",
            "entity": "&#58613;",
            "code": ":poop:",
            "description": "Write bad code that needs to be improved.",
            "name": "poop",
            "semver": "",
        },
        {
            "emoji": "⏪️",
            "entity": "&#9194;",
            "code": ":rewind:",
            "description": "Revert changes.",
            "name": "rewind",
            "semver": "patch",
        },
        {
            "emoji": "🔀",
            "entity": "&#128256;",
            "code": ":twisted_rightwards_arrows:",
            "description": "Merge branches.",
            "name": "twisted-rightwards-arrows",
            "semver": "",
        },
        {
            "emoji": "📦️",
            "entity": "&#1F4E6;",
            "code": ":package:",
            "description": "Add or update compiled files or packages.",
            "name": "package",
            "semver": "patch",
        },
        {
            "emoji": "👽️",
            "entity": "&#1F47D;",
            "code": ":alien:",
            "description": "Update code due to external API changes.",
            "name": "alien",
            "semver": "patch",
        },
        {
            "emoji": "🚚",
            "entity": "&#1F69A;",
            "code": ":truck:",
            "description": "Move or rename resources (e.g.: files, paths, routes).",
            "name": "truck",
            "semver": "",
        },
        {
            "emoji": "📄",
            "entity": "&#1F4C4;",
            "code": ":page_facing_up:",
            "description": "Add or update license.",
            "name": "page-facing-up",
            "semver": "",
        },
        {
            "emoji": "💥",
            "entity": "&#x1f4a5;",
            "code": ":boom:",
            "description": "Introduce breaking changes.",
            "name": "boom",
            "semver": "major",
        },
        {
            "emoji": "🍱",
            "entity": "&#1F371",
            "code": ":bento:",
            "description": "Add or update assets.",
            "name": "bento",
            "semver": "patch",
        },
        {
            "emoji": "♿️",
            "entity": "&#9855;",
            "code": ":wheelchair:",
            "description": "Improve accessibility.",
            "name": "wheelchair",
            "semver": "patch",
        },
        {
            "emoji": "💡",
            "entity": "&#128161;",
            "code": ":bulb:",
            "description": "Add or update comments in source code.",
            "name": "bulb",
            "semver": "",
        },
        {
            "emoji": "🍻",
            "entity": "&#x1f37b;",
            "code": ":beers:",
            "description": "Write code drunkenly.",
            "name": "beers",
            "semver": "",
        },
        {
            "emoji": "💬",
            "entity": "&#128172;",
            "code": ":speech_balloon:",
            "description": "Add or update text and literals.",
            "name": "speech-balloon",
            "semver": "patch",
        },
        {
            "emoji": "🗃️",
            "entity": "&#128451;",
            "code": ":card_file_box:",
            "description": "Perform database related changes.",
            "name": "card-file-box",
            "semver": "patch",
        },
        {
            "emoji": "🔊",
            "entity": "&#128266;",
            "code": ":loud_sound:",
            "description": "Add or update logs.",
            "name": "loud-sound",
            "semver": "",
        },
        {
            "emoji": "🔇",
            "entity": "&#128263;",
            "code": ":mute:",
            "description": "Remove logs.",
            "name": "mute",
            "semver": "",
        },
        {
            "emoji": "👥",
            "entity": "&#128101;",
            "code": ":busts_in_silhouette:",
            "description": "Add or update contributor(s).",
            "name": "busts-in-silhouette",
            "semver": "",
        },
        {
            "emoji": "🚸",
            "entity": "&#128696;",
            "code": ":children_crossing:",
            "description": "Improve user experience / usability.",
            "name": "children-crossing",
            "semver": "patch",
        },
        {
            "emoji": "🏗️",
            "entity": "&#1f3d7;",
            "code": ":building_construction:",
            "description": "Make architectural changes.",
            "name": "building-construction",
            "semver": "",
        },
        {
            "emoji": "📱",
            "entity": "&#128241;",
            "code": ":iphone:",
            "description": "Work on responsive design.",
            "name": "iphone",
            "semver": "patch",
        },
        {
            "emoji": "🤡",
            "entity": "&#129313;",
            "code": ":clown_face:",
            "description": "Mock things.",
            "name": "clown-face",
            "semver": "",
        },
        {
            "emoji": "🥚",
            "entity": "&#129370;",
            "code": ":egg:",
            "description": "Add or update an easter egg.",
            "name": "egg",
            "semver": "patch",
        },
        {
            "emoji": "🙈",
            "entity": "&#8bdfe7;",
            "code": ":see_no_evil:",
            "description": "Add or update a .gitignore file.",
            "name": "see-no-evil",
            "semver": "",
        },
        {
            "emoji": "📸",
            "entity": "&#128248;",
            "code": ":camera_flash:",
            "description": "Add or update snapshots.",
            "name": "camera-flash",
            "semver": "",
        },
        {
            "emoji": "⚗️",
            "entity": "&#x2697;",
            "code": ":alembic:",
            "description": "Perform experiments.",
            "name": "alembic",
            "semver": "patch",
        },
        {
            "emoji": "🔍️",
            "entity": "&#128269;",
            "code": ":mag:",
            "description": "Improve SEO.",
            "name": "mag",
            "semver": "patch",
        },
        {
            "emoji": "🏷️",
            "entity": "&#127991;",
            "code": ":label:",
            "description": "Add or update types.",
            "name": "label",
            "semver": "patch",
        },
        {
            "emoji": "🌱",
            "entity": "&#127793;",
            "code": ":seedling:",
            "description": "Add or update seed files.",
            "name": "seedling",
            "semver": "",
        },
        {
            "emoji": "🚩",
            "entity": "&#x1F6A9;",
            "code": ":triangular_flag_on_post:",
            "description": "Add, update, or remove feature flags.",
            "name": "triangular-flag-on-post",
            "semver": "patch",
        },
        {
            "emoji": "🥅",
            "entity": "&#x1F945;",
            "code": ":goal_net:",
            "description": "Catch errors.",
            "name": "goal-net",
            "semver": "patch",
        },
        {
            "emoji": "💫",
            "entity": "&#x1f4ab;",
            "code": ":dizzy:",
            "description": "Add or update animations and transitions.",
            "name": "animation",
            "semver": "patch",
        },
        {
            "emoji": "🗑️",
            "entity": "&#x1F5D1;",
            "code": ":wastebasket:",
            "description": "Deprecate code that needs to be cleaned up.",
            "name": "wastebasket",
            "semver": "patch",
        },
        {
            "emoji": "🛂",
            "entity": "&#x1F6C2;",
            "code": ":passport_control:",
            "description": "Work on code related to authorization, roles and permissions.",
            "name": "passport-control",
            "semver": "patch",
        },
        {
            "emoji": "🩹",
            "entity": "&#x1FA79;",
            "code": ":adhesive_bandage:",
            "description": "Simple fix for a non-critical issue.",
            "name": "adhesive-bandage",
            "semver": "patch",
        },
        {
            "emoji": "🧐",
            "entity": "&#x1F9D0;",
            "code": ":monocle_face:",
            "description": "Data exploration/inspection.",
            "name": "monocle-face",
            "semver": "",
        },
        {
            "emoji": "⚰️",
            "entity": "&#x26B0;",
            "code": ":coffin:",
            "description": "Remove dead code.",
            "name": "coffin",
            "semver": "",
        },
        {
            "emoji": "🧪",
            "entity": "&#x1F9EA;",
            "code": ":test_tube:",
            "description": "Add a failing test.",
            "name": "test-tube",
            "semver": "",
        },
        {
            "emoji": "👔",
            "entity": "&#128084;",
            "code": ":necktie:",
            "description": "Add or update business logic.",
            "name": "necktie",
            "semver": "patch",
        },
        {
            "emoji": "🩺",
            "entity": "&#x1FA7A;",
            "code": ":stethoscope:",
            "description": "Add or update healthcheck.",
            "name": "stethoscope",
            "semver": "",
        },
        {
            "emoji": "🧱",
            "entity": "&#x1f9f1;",
            "code": ":bricks:",
            "description": "Infrastructure related changes.",
            "name": "bricks",
            "semver": "",
        },
        {
            "emoji": "🧑‍💻",
            "entity": "&#129489;&#8205;&#128187;",
            "code": ":technologist:",
            "description": "Improve developer experience.",
            "name": "technologist",
            "semver": "",
        },
        {
            "emoji": "💸",
            "entity": "&#x1F4B8;",
            "code": ":money_with_wings:",
            "description": "Add sponsorships or money related infrastructure.",
            "name": "money-with-wings",
            "semver": "",
        },
        {
            "emoji": "🧵",
            "entity": "&#x1F9F5;",
            "code": ":thread:",
            "description": "Add or update code related to multithreading or concurrency.",
            "name": "thread",
            "semver": "",
        },
        {
            "emoji": "🦺",
            "entity": "&#x1F9BA;",
            "code": ":safety_vest:",
            "description": "Add or update code related to validation.",
            "name": "safety-vest",
            "semver": "",
        },
    ],
}


def emo_setup():
    global EMODATA

    for e in EMODATA["gitmojis"]:
        e["match_str"] = "".join(e.values())
        e["name"] = e["emoji"] + " " + e["description"]
        e["value"] = e["emoji"]
        e["count"] = 0
    gmp_history.load_history()
    EMODATA = gmp_history.sort_emojis(EMODATA)


def match_emojis(match, fuzzy=False):
    return [
        e
        for e in EMODATA["gitmojis"]
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
            choices=EMODATA["gitmojis"],
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
