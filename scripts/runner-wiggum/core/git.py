"""Git state management for Ralph Wiggum runner.

Provides utilities for branch management, commit automation, and clean state verification
to ensure each story is an atomic, safe unit of work.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable


class GitError(Exception):
    """Base exception for git-related errors."""

    pass


class DirtyWorkingDirectoryError(GitError):
    """Raised when the working directory has uncommitted changes."""

    def __init__(self, status: str):
        self.status = status
        super().__init__(f"Working directory is not clean:\n{status}")


class BranchError(GitError):
    """Raised when branch operations fail."""

    pass


class MergeConflictError(GitError):
    """Raised when a merge conflict occurs."""

    pass


class GitState(Enum):
    """Current state of git operations for a story."""

    CLEAN = "clean"  # Working directory clean, on main
    ON_STORY_BRANCH = "on_story_branch"  # On a wiggum/* branch
    HAS_CHANGES = "has_changes"  # Has uncommitted changes
    MERGE_CONFLICT = "merge_conflict"  # Merge conflict detected


@dataclass
class GitStatus:
    """Represents the current git status."""

    is_clean: bool
    current_branch: str
    has_staged: bool
    has_unstaged: bool
    has_untracked: bool
    is_story_branch: bool
    story_id: str | None = None

    @property
    def state(self) -> GitState:
        """Determine the overall git state."""
        if not self.is_clean:
            return GitState.HAS_CHANGES
        if self.is_story_branch:
            return GitState.ON_STORY_BRANCH
        return GitState.CLEAN


class GitManager:
    """Manages git operations for the runner.

    Ensures each story is developed on an isolated branch and merged back
    cleanly to main upon completion.
    """

    BRANCH_PREFIX = "wiggum"

    def __init__(
        self,
        repo_path: Path,
        main_branch: str = "main",
        on_output: Callable[[str], None] | None = None,
    ):
        """Initialize the git manager.

        Args:
            repo_path: Path to the git repository
            main_branch: Name of the main/default branch (typically 'main' or 'master')
            on_output: Optional callback for logging git operations
        """
        self.repo_path = repo_path
        self.main_branch = main_branch
        self._on_output = on_output

    def _log(self, message: str) -> None:
        """Log a message if callback is set."""
        if self._on_output:
            self._on_output(f"[git] {message}")

    def _run_git(
        self,
        *args: str,
        check: bool = True,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run a git command in the repository.

        Args:
            *args: Git command arguments (e.g., 'status', '--porcelain')
            check: Raise exception on non-zero exit code
            capture_output: Capture stdout/stderr

        Returns:
            CompletedProcess result

        Raises:
            GitError: If the command fails and check=True
        """
        cmd = ["git", *args]
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                check=check,
                capture_output=capture_output,
                text=True,
            )
            return result
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {' '.join(cmd)}\n{e.stderr}") from e

    def is_git_repo(self) -> bool:
        """Check if the path is a git repository."""
        try:
            self._run_git("rev-parse", "--git-dir")
            return True
        except GitError:
            return False

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip()

    def get_status(self) -> GitStatus:
        """Get comprehensive git status information."""
        # Get current branch
        current_branch = self.get_current_branch()

        # Check if on a story branch
        is_story_branch = current_branch.startswith(f"{self.BRANCH_PREFIX}/")
        story_id = None
        if is_story_branch:
            story_id = current_branch[len(f"{self.BRANCH_PREFIX}/") :]

        # Get porcelain status for parsing
        result = self._run_git("status", "--porcelain")
        status_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        has_staged = False
        has_unstaged = False
        has_untracked = False

        for line in status_lines:
            if not line:
                continue
            index_status = line[0]
            worktree_status = line[1]

            if index_status == "?":
                has_untracked = True
            elif index_status != " ":
                has_staged = True

            if worktree_status not in (" ", "?"):
                has_unstaged = True

        is_clean = not (has_staged or has_unstaged or has_untracked)

        return GitStatus(
            is_clean=is_clean,
            current_branch=current_branch,
            has_staged=has_staged,
            has_unstaged=has_unstaged,
            has_untracked=has_untracked,
            is_story_branch=is_story_branch,
            story_id=story_id,
        )

    def check_clean_state(self) -> None:
        """Verify the working directory is clean.

        Raises:
            DirtyWorkingDirectoryError: If there are uncommitted changes
        """
        result = self._run_git("status", "--porcelain")
        if result.stdout.strip():
            # Get human-readable status for error message
            full_status = self._run_git("status", "--short")
            raise DirtyWorkingDirectoryError(full_status.stdout)

    def get_story_branch_name(self, story_id: str) -> str:
        """Get the branch name for a story."""
        return f"{self.BRANCH_PREFIX}/{story_id}"

    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        result = self._run_git(
            "branch", "--list", branch_name, check=False, capture_output=True
        )
        return bool(result.stdout.strip())

    def create_story_branch(self, story_id: str) -> str:
        """Create and switch to a story branch.

        If the branch already exists, switches to it instead.

        Args:
            story_id: The story identifier

        Returns:
            The branch name

        Raises:
            BranchError: If branch creation/switch fails
        """
        branch_name = self.get_story_branch_name(story_id)
        current = self.get_current_branch()

        if current == branch_name:
            self._log(f"Already on branch {branch_name}")
            return branch_name

        try:
            if self.branch_exists(branch_name):
                # Branch exists, switch to it
                self._log(f"Switching to existing branch {branch_name}")
                self._run_git("checkout", branch_name)
            else:
                # Create new branch from main
                self._log(f"Creating new branch {branch_name} from {self.main_branch}")

                # Ensure we're on main before creating branch
                if current != self.main_branch:
                    self._run_git("checkout", self.main_branch)

                self._run_git("checkout", "-b", branch_name)

            return branch_name

        except GitError as e:
            raise BranchError(f"Failed to create/switch to branch {branch_name}: {e}") from e

    def stage_all_changes(self) -> bool:
        """Stage all changes including untracked files.

        Returns:
            True if there were changes to stage, False if clean
        """
        status = self.get_status()
        if status.is_clean:
            return False

        self._log("Staging all changes")
        self._run_git("add", "-A")
        return True

    def commit(self, message: str) -> str | None:
        """Create a commit with the given message.

        Args:
            message: Commit message

        Returns:
            Commit hash if successful, None if nothing to commit
        """
        # Check if there's anything to commit
        result = self._run_git("diff", "--cached", "--quiet", check=False)
        if result.returncode == 0:
            self._log("Nothing to commit")
            return None

        self._log(f"Committing: {message}")
        self._run_git("commit", "-m", message)

        # Get the commit hash
        result = self._run_git("rev-parse", "HEAD")
        return result.stdout.strip()

    def commit_story_completion(self, story_id: str, story_title: str) -> str | None:
        """Stage and commit all changes for a completed story.

        Args:
            story_id: The story identifier
            story_title: The story title for the commit message

        Returns:
            Commit hash if changes were committed, None otherwise
        """
        if not self.stage_all_changes():
            self._log("No changes to commit for story completion")
            return None

        message = f"feat({story_id}): {story_title}"
        return self.commit(message)

    def merge_to_main(self, delete_branch: bool = True) -> bool:
        """Merge current story branch back to main.

        Args:
            delete_branch: Whether to delete the story branch after merge

        Returns:
            True if merge was successful

        Raises:
            MergeConflictError: If merge conflicts occur
            BranchError: If not on a story branch
        """
        status = self.get_status()

        if not status.is_story_branch:
            raise BranchError("Not on a story branch, cannot merge to main")

        story_branch = status.current_branch
        self._log(f"Merging {story_branch} to {self.main_branch}")

        try:
            # Switch to main
            self._run_git("checkout", self.main_branch)

            # Merge the story branch
            self._run_git("merge", story_branch, "--no-ff", "-m", f"Merge branch '{story_branch}'")

            if delete_branch:
                self._log(f"Deleting branch {story_branch}")
                self._run_git("branch", "-d", story_branch)

            return True

        except GitError as e:
            # Check if it's a merge conflict
            if "CONFLICT" in str(e) or "conflict" in str(e).lower():
                raise MergeConflictError(f"Merge conflict when merging {story_branch}") from e
            raise

    def hard_reset_branch(self, story_id: str | None = None) -> None:
        """Hard reset the story branch, discarding all changes.

        Args:
            story_id: Story ID to reset. If None, uses current branch if it's a story branch.

        Raises:
            BranchError: If not on a story branch and no story_id provided
        """
        status = self.get_status()

        if story_id:
            branch_name = self.get_story_branch_name(story_id)
        elif status.is_story_branch:
            branch_name = status.current_branch
        else:
            raise BranchError("Not on a story branch and no story_id provided")

        self._log(f"Hard resetting branch {branch_name}")

        # Discard all local changes
        self._run_git("reset", "--hard", "HEAD")
        self._run_git("clean", "-fd")

    def abort_and_return_to_main(self, story_id: str | None = None) -> None:
        """Abort current work and return to main branch.

        Discards all changes and optionally deletes the story branch.

        Args:
            story_id: Story ID for the branch to clean up
        """
        status = self.get_status()
        branch_to_delete = None

        if story_id:
            branch_to_delete = self.get_story_branch_name(story_id)
        elif status.is_story_branch:
            branch_to_delete = status.current_branch

        # Discard any uncommitted changes
        self._log("Discarding uncommitted changes")
        self._run_git("reset", "--hard", "HEAD", check=False)
        self._run_git("clean", "-fd", check=False)

        # Switch to main
        if status.current_branch != self.main_branch:
            self._log(f"Switching to {self.main_branch}")
            self._run_git("checkout", self.main_branch)

        # Delete the story branch if it exists
        if branch_to_delete and self.branch_exists(branch_to_delete):
            self._log(f"Deleting branch {branch_to_delete}")
            self._run_git("branch", "-D", branch_to_delete)

    def get_uncommitted_changes_summary(self) -> str:
        """Get a summary of uncommitted changes."""
        result = self._run_git("status", "--short")
        return result.stdout.strip()

    def get_diff_stats(self) -> str:
        """Get diff statistics for staged changes."""
        result = self._run_git("diff", "--cached", "--stat", check=False)
        return result.stdout.strip()

    def get_diff_from_main(self) -> str:
        """Get the full diff of changes from the main branch.

        This is useful for review purposes to see all changes made in the story branch.

        Returns:
            The diff output showing all changes from main branch
        """
        result = self._run_git("diff", self.main_branch, "--", check=False)
        return result.stdout.strip()

    def get_diff_stat_from_main(self) -> str:
        """Get diff statistics from the main branch.

        Returns:
            Summary of files changed, insertions, and deletions
        """
        result = self._run_git("diff", self.main_branch, "--stat", check=False)
        return result.stdout.strip()
