"""
Command line interface for gitmopy.
"""
from typing import List, Optional

import git
import typer
from git import Repo
from typing_extensions import Annotated

from gitmopy.git import (
    CatchRemoteException,
    format_remotes_diff,
    get_files_status,
    has_upstreams,
)
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
    CONFIG_PATH,
    HISTORY_PATH,
    _sentinels,
    col,
    console,
    load_config,
    message_from_commit_dict,
    print,
    print_staged_files,
    resolve_path,
    terminal_separator,
)

app = typer.Typer()
gitmojis_setup()


def catch_keyboard_interrupt(func, *args, **kwargs):
    """
    Function to wrap another function in a try/finally block and catch Aborts.

    Executes its first argument with the following arguments and keyword arguments.
    When the function is done (or has been aborted by ctrl+c), it will prompt the
    user to restart the commit process or quit.

    Required because I couldn't find a way to catch typer.Abort exceptions in a
    standard try/except block.

    Args:
        func (Callable): the function to wrap.
        *args (Any): positional arguments to pass to ``func``.
        **kwargs (Any): keyword arguments to pass to ``func``.
    """

    def _func(*_args, **_kwargs):
        """
        Function wrapper that catches typer.Abort exceptions.

        Returns:
            Any: The wrapped function's return value or the ``_sentinels["cancelled"]``
                sentinel if the function was aborted.
        """
        return_value = _sentinels["cancelled"]
        try:
            return_value = func(*_args, **_kwargs)
        finally:
            return return_value

    return_value = _func(*args, **kwargs)
    if return_value is not _sentinels["cancelled"]:
        # function was not aborted
        return return_value

    print(
        "\n[yellow]Press [b green]enter[/b green] to restart commit process"
        + " or [b red]ctrl+c[/b red] again to quit (or [b red]q[/b red]).",
        end="",
    )
    should_stop = typer.prompt(
        "", prompt_suffix="", default="enter", show_default=False
    )

    # at this point if the user presses ctrl+c again, the program will exit

    # user asked to quit
    if should_stop == "q":
        return _sentinels["stop"]

    # user wants to restart the commit process
    print()
    return _sentinels["restart"]


def should_commit_again(repo: Repo, remote: List[str]) -> bool:
    """
    Prompt the user to continue or stop the current commit loop.

    Args:
        repo (Repo): The git repository.

    Returns:
        bool: Whether the user wants to continue or not.
    """
    gitmojis_setup()
    print()
    print(terminal_separator())
    prompt_txt = (
        f"🔄 [u]Ready to commit again[/u]. Press {col('enter', 'g', True)} "
        + "to commit again"
    )

    print()
    remotes_diff = format_remotes_diff(repo)
    if remotes_diff:
        print(remotes_diff)
        prompt_txt += f", {col('p', 'b', True)} to push and commit again,"
        if "does not have a branch" not in remotes_diff:
            prompt_txt += (
                f" {col('s', 'b', True)} to sync (pull then pull)"
                + " and commit again,"
            )

    print(prompt_txt + f" or {col('q', 'r', True)} to quit.", end="")

    commit_again = typer.prompt(
        "", default="enter", show_default=False, prompt_suffix=""
    )
    if remotes_diff:
        if commit_again in {"p", "s"}:
            print()
            if commit_again == "s":
                pull_cli(repo, remote)
            push_cli(repo, remote)
            return should_commit_again(repo, remote)

    commit_again = commit_again != "q"

    if commit_again:
        print()

    return commit_again


def push_cli(repo, remote):
    # push to remotes. If several remotes, use either the values from --remote
    # or prompt the user to choose them.
    # If no remote, ignore push.
    if len(repo.remotes) == 0:
        print(col("No remote found. Ignoring push.", "y"))
    else:
        # default: contain "origin"
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
                print(col("No remote selected. Aborting.", "y"))
                raise typer.Abort()
            selected_remotes = set(selected_remotes)

        with console.status(col("Fetching remotes...", "o")):
            remote_upstreams = has_upstreams(
                repo, selected_remotes, repo.active_branch.name
            )

        # there is at least one remote to push to at this point
        for remote in repo.remotes:
            if remote.name in selected_remotes:
                wait = col(f"Pushing to remote {remote.name}...", "o")
                done = col(f"Pushed to remote {remote.name}", "b", True)
                with console.status(wait):
                    # push to remote, catch exception if it fails to be able to
                    # 1. continue pushing to other remotes
                    # 2. potentially set the upstream branch
                    set_upstream = False
                    if not remote_upstreams[remote.name]:
                        set_upstream = set_upstream_prompt(remote.name)
                    cre = None
                    if set_upstream:
                        with CatchRemoteException(remote.name) as cre:
                            repo.git.push(
                                "--set-upstream",
                                remote.name,
                                repo.active_branch.name,
                            )
                    else:
                        with CatchRemoteException(remote.name) as cre:
                            repo.git.push(remote.name, repo.active_branch.name)
                    if cre and not cre.error:
                        print(done)


def pull_cli(repo, remote_cli_args):
    # pull from remotes. If several remotes, use either the values from --remote
    # or prompt the user to choose them.
    # If no remote, ignore push.
    if len(repo.remotes) == 0:
        print(col("No remote found. Ignoring pull.", "y"))
    else:
        selected_remotes = set([repo.remotes[0].name])
        if len(repo.remotes) > 1:
            if remote_cli_args:
                # use --remote values
                selected_remotes = set(remote_cli_args)
            else:
                # PROMPT: choose remote
                selected_remotes = choose_remote_prompt(repo.remotes)
            if not selected_remotes:
                # stop if no remote selected
                print(col("No remote selected. Aborting.", "y"))
                raise typer.Exit(1)
            selected_remotes = set(selected_remotes)
        print()

        # there is at least one remote to push to at this point
        for remote in repo.remotes:
            if remote.name in selected_remotes:
                wait = col(f"Pulling from remote {remote.name}...", "o")
                done = col(f"Pulled from remote {remote.name}", "b", True)
                with console.status(wait):
                    cre = None
                    with CatchRemoteException(remote.name) as cre:
                        repo.git.pull(remote.name, repo.active_branch.name)
                    if cre and not cre.error:
                        print(done)


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
            to_add = []
            if not dry and not sum([len(v) for v in status.values()]):
                # no files to commit
                print(col("Nothing to commit.", "y"))
                if not keep_alive:
                    # user does not wand to commit continuously
                    raise typer.Exit(0)

                # wait for user input
                if should_commit_again(repo, remote):
                    # user wants to commit again: start over
                    continue
                # user wants to stop: break loop
                break

        if not dry:
            # no staged files and user does not want to add: abort
            if not status["staged"] and not add:
                print(
                    col(
                        +"\nNo staged files. Stage files yourself or use [b]--add[/b]"
                        + " to add all unstaged files.\n",
                        "y",
                    )
                )
                raise typer.Exit(1)
            if remote and not push:
                print(col("\nIgnoring --remote flag because --push is not set\n", "y"))
            # no staged files fbut user wants to add: start prompt
            if not status["staged"] and add:
                # PROMPT: list files to user and add their selection
                to_add = catch_keyboard_interrupt(git_add_prompt, status)
                if to_add is _sentinels["stop"]:
                    break
                elif to_add is _sentinels["restart"]:
                    continue
                elif not to_add:
                    print(col("No file selected, nothing to commit.", "y"))
                    if keep_alive and should_commit_again(repo, remote):
                        # user wants to commit again: start over
                        continue
                    # user wants to stop: break loop
                    break
            else:
                # there are staged files: list them to user
                if add:
                    print(
                        col(
                            "Ignoring --add flag because the stage is not empty.\n", "y"
                        )
                    )

        # load gitmopy's configuraltion from yaml file
        config = load_config()

        # not dry run print files about to be committed
        if not dry:
            print_staged_files(to_add or status["staged"])

        # PROMPT: get user's commit details
        print(f"\n[u]{col('Commit details:', 'g')}[/u]")
        commit_dict = catch_keyboard_interrupt(commit_prompt, config)
        if commit_dict is _sentinels["stop"]:
            break
        elif commit_dict is _sentinels["restart"]:
            continue

        # make commit messsage
        commit_message = message_from_commit_dict(commit_dict)

        if dry:
            # Don't do anything, just print the commit message
            print("\nFormatted commit:\n```")
            print(commit_message)
            print("```")
            raise typer.Exit(0)
        else:
            for f in to_add:
                repo.git.add(f)

        if config["enable_history"]:
            # save commit details to history
            save_to_history(commit_dict)

        # commit
        repo.index.commit(commit_message)

        if push:
            push_cli(repo, remote)

        if keep_alive and should_commit_again(repo, remote):
            # user wants to commit again
            continue
        # stop here
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
    print(f"\n[u]{col('Current configuration:', 'b', True)}[/u]")
    max_l = max([len(k) for k in config.keys()])
    for k, v in config.items():
        print(f"  {k:{max_l}}: {v}")
    print()


if __name__ == "__main__":
    app()
