# `gitmopy`

An interactive Python implementation of the Gitmoji standard: https://gitmoji.dev/

```text
pip install gitmopy
```

![demo-gitmopy](./assets/demo-gitmopy.gif)

## How to use

* I typically use `$ gitmopy commit --add --keep-alive`
* Navigate through options with ⬆️ and ⬇️
* Select option with **`space`**
* Validate selection with **`enter`**
* Press **`tab`** to auto-complete
  * Press `tab` on an empty line to see history
* Restart commit with **`crtl+c`**
  * The keyboard interruption will be caught once, then press `enter` to restart

## Suggested shortcuts

```bash
alias gpy="gitmopy"
alias gpyc="gitmopy commit"
alias gpya="gitmopy commit --add"
alias gpyk="gitmopy commit --add --keep-alive"
```

![gpyk depo](assets/gpyk.png)

## Examples

```bash
# Typical daily use-case
# ----------------------

# continuously commit, interactively select files to stage
$ gitmopy commit --add --keep-alive

# same using an alias, + push after every commit (could be dangerous)
$ gpyk --push


# Specific usage
# --------------

# commit currently staged files. Will fail if no file is staged.
$ gitmopy commit

# Enable interactive file selection if no file is currently staged. Ignored if
# there are staged files.
$ gitmopy commit --add

# Commit continuously: don't leave the CLI after the first commit but restart
# the commit procedure.
$ gitmopy commit --keep-alive

# Push to remote repositories after commit.
# Interactively select remotes to push to if there are more than 1.
$ gitmopy commit --push

# Push to specific remotes
$ gitmopy commit --push --remote origin --remote upstream

# Make and display a commit message without staging/committing/pushing
$ gitmopy commit --dry

# configure gitmopy
$ gitmopy config

# print version, data paths and current configuration
$ gitmopy info

# print helps
$ gitmopy --help
$ gitmopy commit --help
```

⚠️ The sync feature is still experimental. It will `pull` then `push` but in the case of several remotes and the branch not existing on one of them, I recommend you deal with it with `git` manually.

## User guide

```text
$ gitmopy info

gitmopy info:
  version : 0.1.0
  app path: /Users/victor/.gitmopy
  history : /Users/victor/.gitmopy/history.json
  config  : /Users/victor/.gitmopy/config.yaml

Current configuration:
  skip_scope      : False
  skip_message    : False
  capitalize_title: True
  enable_history  : True
```

Update configuration with

```text
$ gitmopy config
$ gitmopy config
❓ Configure gitmopy locally. Use 'space' to (de-)select, 'enter' to validate.
❯ ○ Skip commit scope
  ○ Skip commit message
  ◉ Capitalize commit title
  ◉ Remember commit history for auto-complete and emoji sorting

Config will be saved in /Users/victor/.gitmopy/config.yaml.
```

Get help with

```text
$ gitmopy --help

 Usage: gitmopy [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.             │
│ --show-completion             Show completion for the current shell, to copy it or  │
│                               customize the installation.                           │
│ --help                        Show this message and exit.                           │
╰─────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────╮
│ commit  Commit staged files. Use --add to interactively select files to stage if    │
│         none is already staged                                                      │
│ config  Configure gitmopy                                                           │
│ info    Print gitmopy info                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────╯

$ gitmopy commit --help

 Usage: gitmopy commit [OPTIONS]

 Commit staged files. Use --add to interactively select files to stage if none is
 already staged

╭─ Options ───────────────────────────────────────────────────────────────────────────╮
│ --repo                             TEXT  Path to the git repository [default: .]    │
│ --add           --no-add                 Whether or not to interactively select     │
│                                          files to stage if none is already staged   │
│                                          [default: no-add]                          │
│ --push          --no-push                Whether to `git push` after commit. If     │
│                                          multiple remotes exist, you will be asked  │
│                                          to interactively choose the ones to push   │
│                                          to. Use --remote to skip interactive       │
│                                          selection. Disabled by default.            │
│                                          [default: no-push]                         │
│ --dry           --no-dry                 Whether or not to actually commit.         │
│                                          [default: no-dry]                          │
│ --remote                           TEXT  Remote to push to after commit. Use to     │
│                                          skip interactive remote selection when     │
│                                          several exist. Use several '--remote       │
│                                          {remote name}' to push to multiple remotes │
│ --keep-alive    --no-keep-alive          Whether or not to keep the app alive after │
│                                          commit, to be ready for another one.       │
│                                          [default: no-keep-alive]                   │
│ --help                                   Show this message and exit.                │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

## To Do

* Features
  * *If requested:*
    * Install hook
    * `git commit` flags (like `-S`)
    * max history length (if loading the json becomes slow)
* Tests
  * https://typer.tiangolo.com/tutorial/testing/
  * 👋 **Help wanted**
* Docs
  * Not critical

## Resources

`gitmopy` is inspired by [`gitmoji-cli`](https://github.com/carloscuesta/gitmoji-cli).

It is built thanks to:

* [`typer`](https://github.com/tiangolo/typer)
* [`InquirePy`](https://github.com/kazhala/InquirerPy)
* [`GitPython`](https://github.com/gitpython-developers/GitPython)
