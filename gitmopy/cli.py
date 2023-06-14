import git
import typer
from typing_extensions import Annotated
from rich import print

from gitmopy.prompt import commit_prompt, setup_prompt, git_add_prompt
from gitmopy.utils import resolve_path, load_config, print_staged_files
from gitmopy.history import save_to_history

app = typer.Typer()


def get_staged(repo):
    return [item.a_path for item in repo.index.diff("HEAD")]


def get_unstaged(repo):
    return [item.a_path for item in repo.index.diff(None)]


def get_untracked(repo):
    return [item for item in repo.untracked_files]


def get_files_status(repo):
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
    # push: Annotated[
    #     str,
    #     typer.Option(
    #         help="Where to push after the commit (for instance: 'origin master)."
    #         + "Quotes must be used. Disabled by default."
    #     ),
    # ] = None,
    dry: Annotated[
        bool, typer.Option(help="Whether or not to actually commit.")
    ] = False,
):
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
    cd = commit_prompt(config)

    commit_message = (
        f"{cd['emoji']} ({cd['scope']}): {cd['title']}\n\n{cd['message']}"
        if cd["scope"]
        else f"{cd['emoji']} {cd['title']}\n\n{cd['message']}"
    ).strip()

    if dry:
        print("\nFormatted commit:\n```")
        print(commit_message)
        print("```")
        raise typer.Exit(0)

    if config["enable_history"]:
        save_to_history(cd)

    repo.index.commit(commit_message)

    # if push == "":
    #     typer.echo("Pushing to origin...")
    #     origin = repo.remote(name="origin")
    #     origin.push()
    # elif push is not None:
    #     typer.echo(f"Pushing to {push}...")
    #     dest, branch = push.split(" ")
    #     repo.git.push(dest, branch)
    print("\nDone 🥳\n")


@app.command(
    help="Configure gitmopy",
)
def setup():
    setup_prompt()


@app.command(
    help="Print version",
)
def version():
    import gitmopy

    print(gitmopy.__version__)


if __name__ == "__main__":
    app()
