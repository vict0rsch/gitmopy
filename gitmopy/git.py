"""
`gitmopy`'s Git-related utility functions.
"""
from typing import Dict, List, Union

from git import Remote, Repo
from git.exc import GitCommandError

from gitmopy.constants import _sentinels
from gitmopy.utils import col, print


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
            print(
                f"[bold red]Error:[/bold red] could not push to {self.remote}:",
            )
            print("[red]" + exc_value.stderr + "[/red]")

        return True


def fetch_all(repo):
    """
    Fetch all remotes of a GitPython repository.

    Args:
        repo (git.Repo): Repository to fetch remotes from.
    """
    for r in repo.remotes:
        r.fetch()


def has_upstreams(
    repo: Repo, remotes: List[Union[str, Remote]], branch_name: str
) -> Dict[str, bool]:
    """
    Check which remotes have a branch with a given name.

    Args:
        repo (git.Repo): Repository to check branches from.
        remotes (List[Union[str, Remote]]): List of remotes to check.
        branch_name (str): Name of the branch to check.

    Returns:
        Dict[str, bool]: Dictionnary of booleans indicating if each remote has the
            branch.
    """
    fetch_all(repo)
    remote_has_upstream = {
        r.name if isinstance(r, Remote) else r: False for r in remotes
    }
    remote_refs = {
        ref.remote_name: True
        for ref in repo.refs
        if ref.is_remote()
        and ref.name.removeprefix(ref.remote_name + "/") == branch_name
    }
    remote_has_upstream.update(remote_refs)

    return remote_has_upstream


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
    behinds = {}
    for r in repo.remotes:
        try:
            behinds[r.name] = len(list(repo.iter_commits(f"{b}..{r.name}/{b}")))
        except GitCommandError as e:
            if "fatal: bad revision" in str(e):
                behinds[r.name] = _sentinels["no-branch"]
    return behinds


def commits_ahead(repo: Repo) -> int:
    """
    Get the number of commits the local current branch is behind for each remote.

    Args:
        repo (Repo): GitPython repository object.

    Returns:
        int: Number of commits the local current branch is behind for each remote.
    """
    b = repo.active_branch.name
    aheads = {}
    for r in repo.remotes:
        try:
            aheads[r.name] = len(list(repo.iter_commits(f"{r.name}/{b}..{b}")))
        except GitCommandError:
            # already caught and printed in commits_behind
            pass
    return aheads


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

    no_branch = [k for k, v in behind.items() if v is _sentinels["no-branch"]]

    if (
        not (
            sum([b for b in behind.values() if b is not _sentinels["no-branch"]])
            + sum(ahead.values())
        )
        and not no_branch
    ):
        return ""

    s = f"[u]{col('Remotes diff:', 'g')}[/u]\n"
    for r in repo.remotes:
        if behind[r.name]:
            if behind[r.name] is _sentinels["no-branch"]:
                b = repo.active_branch
                s += col(f"remote {r.name} does not have a branch {b}\n", "y")
                continue
            s += col(
                f"  ↵ local is behind {r.name} by {behind[r.name]} commit(s)\n", "o"
            )
        if ahead[r.name]:
            s += col(
                f"  ↳ local is ahead of {r.name} by {ahead[r.name]} commit(s)\n", "p"
            )

    return s
