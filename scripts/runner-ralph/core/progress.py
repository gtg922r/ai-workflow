"""Progress and session logging for Runner Ralph."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Pattern to extract decisions/learnings from agent output
DECISION_PATTERN = re.compile(r"<decision>(.*?)</decision>", re.DOTALL | re.IGNORECASE)
LEARNING_PATTERN = re.compile(r"<learning>(.*?)</learning>", re.DOTALL | re.IGNORECASE)


@dataclass
class RunRecord:
    """Record of a single agent run."""

    iteration: int
    story_id: str | None
    started_at: datetime
    ended_at: datetime | None = None
    success: bool = False
    summary: str = ""
    tokens_used: int | None = None
    cost: float | None = None
    error: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Duration of the run in seconds."""
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None

    def format_summary(self) -> str:
        """Format a human-readable summary of the run."""
        status = "✓" if self.success else "✗"
        duration = f"{self.duration_seconds:.1f}s" if self.duration_seconds else "?"
        story = f"[{self.story_id}]" if self.story_id else "[no story]"

        parts = [f"{status} Run #{self.iteration} {story} ({duration})"]

        if self.tokens_used:
            parts.append(f"  Tokens: {self.tokens_used:,}")
        if self.cost:
            parts.append(f"  Cost: ${self.cost:.4f}")
        if self.summary:
            parts.append(f"  {self.summary}")
        if self.error:
            parts.append(f"  Error: {self.error}")

        return "\n".join(parts)


@dataclass
class ProgressLogger:
    """Manages progress logging and session state."""

    session_id: str
    project_path: Path
    runs: list[RunRecord] = field(default_factory=list)
    learnings: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def progress_file(self) -> Path:
        """Path to the progress.txt file."""
        return self.project_path / "progress.txt"

    @property
    def session_file(self) -> Path:
        """Path to the session.txt file."""
        return self.project_path / "session.txt"

    def initialize(self) -> None:
        """Initialize the progress file if it doesn't exist."""
        if not self.progress_file.exists():
            header = (
                f"# Progress Log - {self.session_id}\n"
                f"# Started: {self.started_at.isoformat()}\n"
                f"# Project: {self.project_path.name}\n"
                "---\n"
            )
            self.progress_file.write_text(header)

    def start_run(self, iteration: int, story_id: str | None = None) -> RunRecord:
        """Start a new run and return the record."""
        record = RunRecord(
            iteration=iteration,
            story_id=story_id,
            started_at=datetime.now(),
        )
        self.runs.append(record)
        self._update_session_file()
        return record

    def end_run(
        self,
        record: RunRecord,
        success: bool,
        summary: str = "",
        tokens_used: int | None = None,
        cost: float | None = None,
        error: str | None = None,
    ) -> None:
        """Complete a run record."""
        record.ended_at = datetime.now()
        record.success = success
        record.summary = summary
        record.tokens_used = tokens_used
        record.cost = cost
        record.error = error
        self._update_session_file()

    def add_learning(self, learning: str) -> None:
        """Add a learning to the progress log."""
        self.learnings.append(learning)
        self._append_to_progress(f"💡 Learning: {learning}")

    def log_run_completion(self, record: RunRecord) -> None:
        """Log a run completion to the progress file."""
        status = "✓ Completed" if record.success else "✗ Failed"
        story_info = f" [{record.story_id}]" if record.story_id else ""
        duration = f" ({record.duration_seconds:.1f}s)" if record.duration_seconds else ""

        entry = f"Run #{record.iteration}{story_info}: {status}{duration}"
        if record.summary:
            entry += f"\n   Summary: {record.summary}"
        if record.error:
            entry += f"\n   Error: {record.error}"

        self._append_to_progress(entry)

    def log_review(self, story_id: str, verdict: str, review_output: str) -> None:
        """Log a review result to the progress file.

        Args:
            story_id: The story that was reviewed
            verdict: The review verdict (approve/reject/unknown)
            review_output: The full review output from the agent
        """
        # Determine icon based on verdict
        icon = "✓" if verdict == "approve" else "✗" if verdict == "reject" else "?"
        header = f"{icon} Review [{story_id}]: {verdict.upper()}"

        # Truncate review output if too long for readability
        max_length = 2000
        if len(review_output) > max_length:
            truncated = review_output[:max_length] + f"\n... (truncated, {len(review_output) - max_length} chars omitted)"
        else:
            truncated = review_output

        entry = f"{header}\n   Review Output:\n{truncated}"
        self._append_to_progress(entry)

    def log_story_completion(
        self,
        story_id: str,
        story_title: str,
        worklog_summary: str | None = None,
    ) -> None:
        """Log a story completion with optional worklog summary.

        Args:
            story_id: The completed story's ID
            story_title: The story title
            worklog_summary: Optional summary from the worklog
        """
        header = f"✓ Story Completed [{story_id}]: {story_title}"

        if worklog_summary:
            entry = f"{header}\n{worklog_summary}"
        else:
            entry = header

        self._append_to_progress(entry)

    def extract_decisions_from_output(self, output: str) -> list[str]:
        """Extract decision/learning markers from agent output and log them."""
        decisions: list[str] = []

        # Extract <decision>...</decision> markers
        for match in DECISION_PATTERN.finditer(output):
            decision = match.group(1).strip()
            if decision:
                decisions.append(decision)
                self._append_to_progress(f"📋 Decision: {decision}")

        # Extract <learning>...</learning> markers
        for match in LEARNING_PATTERN.finditer(output):
            learning = match.group(1).strip()
            if learning:
                decisions.append(learning)
                self.learnings.append(learning)
                self._append_to_progress(f"💡 Learning: {learning}")

        return decisions

    def _append_to_progress(self, content: str) -> None:
        """Append content to the progress.txt file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}] {content}\n"

        with self.progress_file.open("a") as f:
            f.write(entry)

    def _update_session_file(self) -> None:
        """Update the session.txt file with current state."""
        lines = [
            f"Session: {self.session_id}",
            f"Started: {self.started_at.isoformat()}",
            f"Last Update: {datetime.now().isoformat()}",
            f"Total Runs: {len(self.runs)}",
            "",
            "--- Run History ---",
        ]

        for run in self.runs[-10:]:  # Last 10 runs
            lines.append(run.format_summary())
            lines.append("")

        with self.session_file.open("w") as f:
            f.write("\n".join(lines))

    def load_existing_progress(self) -> str:
        """Load existing progress content if available."""
        if self.progress_file.exists():
            return self.progress_file.read_text()
        return ""

    @property
    def total_runs(self) -> int:
        """Total number of runs."""
        return len(self.runs)

    @property
    def successful_runs(self) -> int:
        """Number of successful runs."""
        return sum(1 for r in self.runs if r.success)

    @property
    def failed_runs(self) -> int:
        """Number of failed runs."""
        return sum(1 for r in self.runs if not r.success and r.ended_at)

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all runs."""
        return sum(r.tokens_used or 0 for r in self.runs)

    @property
    def total_cost(self) -> float:
        """Total cost across all runs."""
        return sum(r.cost or 0 for r in self.runs)

    @property
    def last_run(self) -> RunRecord | None:
        """Get the most recent run."""
        return self.runs[-1] if self.runs else None

    def get_stats(self) -> dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "duration_seconds": (datetime.now() - self.started_at).total_seconds(),
        }

