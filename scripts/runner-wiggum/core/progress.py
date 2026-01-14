"""Progress and session logging for Ralph Wiggum runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


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
        self._append_to_progress(learning)

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

