from typing import Dict, List

import git
import typer
from git import Repo
from rich import print
from typing_extensions import Annotated

from gitmopy.history import gitmojis_setup, save_to_history
from gitmopy.prompt import (
    choose_remote_prompt,
    commit_prompt,
    config_prompt,
    git_add_prompt,
)
from gitmopy.utils import (
    APP_PATH,
    HISTORY_PATH,
    CONFIG_PATH,
    load_config,
    message_from_commit_dict,
    print_staged_files,
    resolve_path,
)

app = typer.Typer()
gitmojis_setup()


def get_staged(repo: Repo) -> List[str]:
    """
    Get staged files from a GitPython repository.

    Args:
        repo (git.Repo): Repository to get staged files from.

    Returns:
        List[str]: File paths of staged files.
    """
    return [item.a_path for item in repo.index.diff("HEAD")]


def get_unstaged(repo: Repo) -> List[str]:
    """
    Get unstaged files from a GitPython repository.

    Args:
        repo (git.Repo): Repository to get unstaged files from.

    Returns:
        List[str]: File paths of unstaged files.
    """
    return [item.a_path for item in repo.index.diff(None)]


def get_untracked(repo: Repo) -> List[str]:
    """
    Get untracked files from a GitPython repository.

    Args:
        repo (git.Repo): Repository to get untracked files from.

    Returns:
        List[str]: File paths of untracked files.
    """
    return [item for item in repo.untracked_files]


def get_files_status(repo: Repo) -> Dict[str, List[str]]:
    """
    Make a dictionnary of the files' status in a GitPython repository.
    Keys are "staged", "unstaged" and "untracked".
    Values are lists of file paths.

    Args:
        repo (git.Repo): Repository to get files' status from.

    Returns:
        Dict[str, List[str]]: Dictionnary of files' status.
    """
    return {
        "staged": get_staged(repo),
        "unstaged": get_unstaged(repo),
        "untracked": get_untracked(repo),
    }


@app.command(
    help="Commit staged files. Use --add to add all"
    + " unstaged files if none is already staged",
)
def commit(
    repo: Annotated[str, typer.Option(help="Path to the git repository")] = ".",
    add: Annotated[
        bool,
        typer.Option(
            help="Whether or not to add all unstaged files if none is already staged"
        ),
    ] = False,
    push: Annotated[
        bool,
        typer.Option(help="Whether to `git push` after commit. Disabled by default."),
    ] = None,
    dry: Annotated[
        bool, typer.Option(help="Whether or not to actually commit.")
    ] = False,
):
    """
    Main command: commit staged files, and staging files if need be.

    Args:
        repo (str, optional): Path to the git repository. Defaults to ".".
        add (bool, optional): Whether or not to select unstaged files to add
            if none is already staged. Defaults to False.
        dry (bool, optional): Whether or not to actually commit.
            Defaults to False.

    Raises:
        typer.Exit: Path to repository is not a Git repository.
        typer.Exit: No staged files and user does not want to add.
        typer.Exit: User asked for a dry run.
    """
    # resolve repository path
    repo_path = resolve_path(repo)
    repo_ok = False
    # load repo from path
    try:
        repo = git.Repo(str(repo_path))
        repo_ok = True
    except git.exc.InvalidGitRepositoryError:
        if not dry:
            rp = typer.style(str(repo_path), bg=typer.colors.RED)
            mess = typer.style(" is not a valid git repository.", fg=typer.colors.RED)
            typer.echo(rp + mess)
            raise typer.Exit(1)
    if repo_ok:
        # get current files' status
        status = get_files_status(repo)

    if not dry:
        # no staged files and user does not want to add: abort
        if not status["staged"] and not add:
            print(
                "[yellow]"
                + "No staged files. Stage files yourself or use [b]--add[/b]"
                + " to add all unstaged files.[/yellow]"
            )
            raise typer.Exit(1)
        # no staged files fbut user wants to add: start prompt
        if not status["staged"] and add:
            # PROMPT: list files to user and add their selection
            to_add = git_add_prompt(status)
            for f in to_add:
                repo.git.add(f)
            print_staged_files(to_add)
        else:
            # there are staged files: list them to user
            if add:
                print(
                    "[yellow]Ignoring --add flag because the stage is"
                    + " not empty[/yellow]\n"
                )
            print_staged_files(status["staged"])

    # load gitmopy's configuraltion from yaml file
    config = load_config()

    # PROMPT: get user's commit details
    print("\n[u green3]Commit details:[/u green3]")
    commit_dict = commit_prompt(config)

    # make commit messsage
    commit_message = message_from_commit_dict(commit_dict)

    if dry:
        # Don't do anything, just print the commit message
        print("\nFormatted commit:\n```")
        print(commit_message)
        print("```")
        raise typer.Exit(0)

    if config["enable_history"]:
        # save commit details to history
        save_to_history(commit_dict)

    # commit
    repo.index.commit(commit_message)

    if push:
        if len(repo.remotes) > 1:
            # PROMPT: choose remote
            selected_remotes = choose_remote_prompt(repo.remotes)
            if not selected_remotes:
                print("[yellow]No remote selected. Aborting.[/yellow]")
                raise typer.Exit(1)
            selected_remotes = set(selected_remotes)
            for remote in repo.remotes:
                if remote.name in selected_remotes:
                    remote.push()
        elif len(repo.remotes) == 0:
            print("[yellow]No remote found. Ignoring push.[/yellow]")
        else:
            remote_name = repo.remotes[0].name
            print(f"\n[dodger_blue3]Pushing to remote {remote_name}[/dodger_blue3]")
            repo.remotes[0].push()
    print("\nDone 🥳\n")


@app.command(
    help="Configure gitmopy",
)
def config():
    """
    Command to setup gitmopy's configuration.
    """
    config_prompt()


@app.command(
    help="Print gitmopy info",
)
def info():
    """
    Command to print gitmopy's info.
    """
    import gitmopy

    print("\n[b u green3]gitmopy info:[/b u green3]")
    print("  version :", gitmopy.__version__)
    print("  app path:", str(APP_PATH))
    if HISTORY_PATH.exists():
        print("  history :", str(HISTORY_PATH))
    if CONFIG_PATH:
        print("  config  :", str(CONFIG_PATH))
    config = load_config()
    print("\n[b u green3]Current configuration:[/b u green3]")
    max_l = max([len(k) for k in config.keys()])
    for k, v in config.items():
        print(f"  {k:{max_l}}: {v}")
    print()


if __name__ == "__main__":
    app()
