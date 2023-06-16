"""
`gitmopy`'s Git-related utility functions.
"""
from typing import Dict, List

from git import Repo
from git.exc import GitCommandError


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
        if exc_type is GitCommandError:
            self.error = True
            self.set_upsteam = "has no upstream branch" in exc_value.stderr
            print(
                f"[bold red]Error:[/bold red] could not push to {self.remote}:",
            )
            print("[red]" + exc_value.stderr + "[/red]")

        return True


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


def unstage(repo: Repo, files: List[str]) -> None:
    """
    Unstage files from the index.

    Args:
        repo (Repo): GitPython repository object.
        files (List[str]): List of files to unstage.
    """
    for f in files:
        repo.git.restore("--staged", f)


def commits_behind(repo: Repo) -> int:
    """
    Get the number of commits the local current branch is behind for each remote.

    Args:
        repo (Repo): GitPython repository object.

    Returns:
        int: Number of commits the local current branch is behind for each remote.
    """
    b = repo.active_branch.name
    return {
        r.name: len(list(repo.iter_commits(f"{b}..{r.name}/{b}"))) for r in repo.remotes
    }


def commits_ahead(repo: Repo) -> int:
    """
    Get the number of commits the local current branch is behind for each remote.

    Args:
        repo (Repo): GitPython repository object.

    Returns:
        int: Number of commits the local current branch is behind for each remote.
    """
    b = repo.active_branch.name
    return {
        r.name: len(list(repo.iter_commits(f"{r.name}/{b}..{b}"))) for r in repo.remotes
    }


def format_remotes_diff(repo: Repo) -> str:
    """
    Format the remotes diff.

    Args:
        repo (Repo): GitPython repository object.

    Returns:
        str: Formatted remotes diff.
    """
    behind = commits_behind(repo)
    ahead = commits_ahead(repo)

    if not (sum(behind.values()) + sum(ahead.values())):
        return ""

    s = "[u green]Remotes diff:[/u green]\n"
    for r in repo.remotes:
        if behind[r.name]:
            s += f"[orange3]behind {r.name} by {behind[r.name]} commit(s)[/orange3]\n"
        if ahead[r.name]:
            s += f"[plum3]ahead {r.name} by {ahead[r.name]} commit(s)[/plum3]\n"

    return s
