"""
Command line interface for gitmopy.
"""
from typing import Dict, List, Optional

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
    set_upstream_prompt,
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


class CatchRemoteException:
    def __init__(self, remote: str):
        """
        Context manager to catch GitCommandError when pushing to a remote.

        Also stores whether the issue is that the remote has no upstream branch.

        Args:
            remote (str): Name of the remote repository that is being pushed to.
        """
        self.remote = remote
        self.error = False
        self.set_upsteam = False

    def __enter__(self):
        """
        Enter the context manager.

        Returns:
            CatchRemoteException: the context manager itself.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager and catch a potential GitCommandError exception.

        Prints the error in red.
        If the error is that the remote has no upstream branch, store a ``bool``
        attribute to tell the CLI it should ask the user if they want to set it up.

        Args:
            exc_type (BaseException): Exception type
            exc_value (BaseException): Exception value
            traceback (TracebackType): _description_

        Returns:
            bool: True. This allows to always catch the exception.
        """
        if exc_type is git.exc.GitCommandError:
            self.error = True
            self.set_upsteam = "has no upstream branch" in exc_value.stderr
            print(
                f"[bold red]Error:[/bold red] could not push to {self.remote}:",
            )
            print("[red]" + exc_value.stderr + "[/red]")

        return True



def patched_commit_prompt(repo: Repo, config: Dict[str, bool]) -> Dict[str, str]:
    def _catched_prompt():
        commit = None
        try:
            commit = commit_prompt(config)
            print("commit_prompt: ", commit)
        finally:
            return commit

    while True:
        commit = _catched_prompt()
        if commit:
            return commit
        print("\n[yellow]Quit (q) or commit again (enter)?[/yellow]")
        should_stop = typer.prompt("q / enter", default="enter")
        if should_stop == "q":
            # cancel_commit(repo)
            break
        else:
            print()


def should_continue() -> bool:
    """
    Prompt the user to continue or stop the current commit loop.

    Returns:
        bool: Whether the user wants to continue or not.
    """
    print(
        "\nReady to commit again. Press [orange3]q[/orange3] to quit, "
        + "[green]enter[/green] to commit again"
    )
    should_stop = typer.prompt("q / enter", default="enter")
    return should_stop != "q"


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
    help="Commit staged files. Use --add to interactively select files to"
    + " stage if none is already staged",
)
def commit(
    repo: Annotated[str, typer.Option(help="Path to the git repository")] = ".",
    add: Annotated[
        bool,
        typer.Option(
            help="Whether or not to interactively select files to"
            + " stage if none is already staged"
        ),
    ] = False,
    push: Annotated[
        bool,
        typer.Option(
            help="Whether to `git push` after commit. If multiple remotes exist, "
            + "you will be asked to interactively choose the ones to push to. "
            + "Use --remote to skip interactive selection. Disabled by default."
        ),
    ] = None,
    dry: Annotated[
        bool, typer.Option(help="Whether or not to actually commit.")
    ] = False,
    remote: Annotated[
        Optional[List[str]],
        typer.Option(
            help="Remote to push to after commit. Use to skip interactive remote"
            + " selection when several exist. Use several '--remote {remote name}' "
            + "to push to multiple remotes"
        ),
    ] = [],
    keep_alive: Annotated[
        Optional[bool],
        typer.Option(
            help="Whether or not to keep the app alive after commit, to be ready "
            + "for another one. "
        ),
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
    repo_str = str(repo)
    while True:
        # resolve repository path
        repo = repo_str
        repo_path = resolve_path(repo)
        repo_ok = False
        # load repo from path
        try:
            repo = git.Repo(str(repo_path))
            repo_ok = True
        except git.exc.InvalidGitRepositoryError:
            if not dry:
                rp = typer.style(str(repo_path), bg=typer.colors.RED)
                mess = typer.style(
                    " is not a valid git repository.", fg=typer.colors.RED
                )
                typer.echo(rp + mess)
                raise typer.Exit(1)
        if repo_ok:
            # get current files' status
            status = get_files_status(repo)
            if not dry and not sum([len(v) for v in status.values()]):
                # no files to commit
                if not keep_alive:
                    # user does not wand to commit continuously
                    print("[yellow]Nothing to commit.[/yellow]")
                    raise typer.Exit(0)

                # wait for user input
                if should_continue():
                    # user wants to commit again: start over
                    continue
                # user wants to stop: break loop
                break

        if not dry:
            # no staged files and user does not want to add: abort
            if not status["staged"] and not add:
                print(
                    "\n[yellow]"
                    + "No staged files. Stage files yourself or use [b]--add[/b]"
                    + " to add all unstaged files.[/yellow]\n"
                )
                raise typer.Exit(1)
            if remote and not push:
                print(
                    "\n[yellow]Ignoring --remote flag because --push is not set[/yellow]\n"
                )
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
        commit_dict = patched_commit_prompt(repo, config)
        if not commit_dict:
            break

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
            # push to remotes. If several remotes, use either the values from --remote
            # or prompt the user to choose them.
            # If no remote, ignore push.
            if len(repo.remotes) == 0:
                print("[yellow]No remote found. Ignoring push.[/yellow]")
            else:
                selected_remotes = set([repo.remotes[0].name])
                if len(repo.remotes) > 1:
                    if remote:
                        # use --remote values
                        selected_remotes = set(remote)
                    else:
                        # PROMPT: choose remote
                        selected_remotes = choose_remote_prompt(repo.remotes)
                    if not selected_remotes:
                        # stop if no remote selected
                        print("[yellow]No remote selected. Aborting.[/yellow]")
                        raise typer.Exit(1)
                    selected_remotes = set(selected_remotes)
                print()
                color = "dodger_blue3"

                # there is at least one remote to push to at this point
                for remote in repo.remotes:
                    if remote.name in selected_remotes:
                        print(
                            f"[{color}]Pushing to remote {remote.name}[/{color}]",
                        )
                        # push to remote, catch exception if it fails to be able to
                        # 1. continue pushing to other remotes
                        # 2. potentially set the upstream branch
                        with CatchRemoteException(remote.name) as cre:
                            repo.git.push(remote.name, repo.active_branch.name)
                        if cre.set_upsteam:
                            set_upstream = set_upstream_prompt(remote.name)
                            if set_upstream:
                                # user wants to set the upstream branch: try again
                                with CatchRemoteException(remote.name) as cre:
                                    repo.git.push(
                                        "--set-upstream",
                                        remote.name,
                                        repo.active_branch.name,
                                    )

        if not keep_alive or not should_continue():
            # user did not set the --keep-alive flag or does not want to continue:
            # we're done.
            break

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
