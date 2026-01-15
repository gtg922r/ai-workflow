"""Work log management for per-iteration tracking.

Provides append-only logging for each story's work progress, including
plans, todos, decisions, and progress updates. Supports real-time UI updates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable


class EntryType(Enum):
    """Type of work log entry."""

    PLAN = "plan"
    TODO = "todo"
    TODO_COMPLETE = "todo_complete"
    DECISION = "decision"
    LEARNING = "learning"
    PROGRESS = "progress"
    OUTPUT = "output"
    ERROR = "error"


@dataclass
class WorkLogEntry:
    """A single entry in the work log."""

    timestamp: datetime
    entry_type: EntryType
    content: str
    metadata: dict = field(default_factory=dict)

    def format_time(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime("%H:%M:%S")

    def format_line(self) -> str:
        """Format entry as a single line for display."""
        prefix = {
            EntryType.PLAN: "📋",
            EntryType.TODO: "☐",
            EntryType.TODO_COMPLETE: "☑",
            EntryType.DECISION: "🔧",
            EntryType.LEARNING: "💡",
            EntryType.PROGRESS: "→",
            EntryType.OUTPUT: "📤",
            EntryType.ERROR: "❌",
        }.get(self.entry_type, "•")

        return f"[{self.format_time()}] {prefix} {self.content}"

    def to_markdown(self) -> str:
        """Format entry as markdown."""
        time_str = self.format_time()

        if self.entry_type == EntryType.PLAN:
            return f"\n### Plan\n{self.content}\n"
        elif self.entry_type == EntryType.TODO:
            return f"- [ ] {self.content}"
        elif self.entry_type == EntryType.TODO_COMPLETE:
            return f"- [x] {self.content}"
        elif self.entry_type == EntryType.DECISION:
            return f"- **Decision** [{time_str}]: {self.content}"
        elif self.entry_type == EntryType.LEARNING:
            return f"- **Learning** [{time_str}]: {self.content}"
        elif self.entry_type == EntryType.ERROR:
            return f"- **Error** [{time_str}]: {self.content}"
        else:
            return f"[{time_str}] {self.content}"


class WorkLog:
    """Manages work log for a single story iteration.

    Provides append-only logging with real-time notifications and
    markdown file persistence.
    """

    # Patterns to extract structured info from agent output
    DECISION_PATTERN = re.compile(r"<decision>(.*?)</decision>", re.IGNORECASE | re.DOTALL)
    LEARNING_PATTERN = re.compile(r"<learning>(.*?)</learning>", re.IGNORECASE | re.DOTALL)
    TODO_PATTERN = re.compile(r"^[-*]\s*\[\s*\]\s*(.+)$", re.MULTILINE)
    TODO_DONE_PATTERN = re.compile(r"^[-*]\s*\[x\]\s*(.+)$", re.MULTILINE | re.IGNORECASE)

    def __init__(
        self,
        story_id: str,
        story_title: str,
        worklog_dir: Path,
        on_entry: Callable[[WorkLogEntry], None] | None = None,
    ):
        """Initialize work log for a story.

        Args:
            story_id: Unique identifier for the story
            story_title: Human-readable story title
            worklog_dir: Directory to store worklog files
            on_entry: Optional callback for real-time entry notifications
        """
        self.story_id = story_id
        self.story_title = story_title
        self.worklog_dir = worklog_dir
        self.path = worklog_dir / f"{story_id}.md"
        self.entries: list[WorkLogEntry] = []
        self._on_entry = on_entry
        self._started = datetime.now()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the worklog file with header."""
        if self._initialized:
            return

        self.worklog_dir.mkdir(parents=True, exist_ok=True)

        header = f"""# Work Log: {self.story_id}
## {self.story_title}

Started: {self._started.strftime("%Y-%m-%d %H:%M:%S")}

---

## Progress

"""
        self.path.write_text(header)
        self._initialized = True

    def append(
        self,
        entry_type: EntryType,
        content: str,
        metadata: dict | None = None,
    ) -> WorkLogEntry:
        """Append an entry to the work log.

        Args:
            entry_type: Type of entry
            content: Entry content
            metadata: Optional additional metadata

        Returns:
            The created entry
        """
        if not self._initialized:
            self.initialize()

        entry = WorkLogEntry(
            timestamp=datetime.now(),
            entry_type=entry_type,
            content=content.strip(),
            metadata=metadata or {},
        )
        self.entries.append(entry)

        # Append to file (append-only)
        with self.path.open("a") as f:
            f.write(entry.to_markdown() + "\n")

        # Notify callback
        if self._on_entry:
            self._on_entry(entry)

        return entry

    def log_progress(self, message: str) -> WorkLogEntry:
        """Log a progress update."""
        return self.append(EntryType.PROGRESS, message)

    def log_decision(self, decision: str) -> WorkLogEntry:
        """Log an architectural decision."""
        return self.append(EntryType.DECISION, decision)

    def log_learning(self, learning: str) -> WorkLogEntry:
        """Log a learning/insight."""
        return self.append(EntryType.LEARNING, learning)

    def log_error(self, error: str) -> WorkLogEntry:
        """Log an error."""
        return self.append(EntryType.ERROR, error)

    def log_todo(self, todo: str, complete: bool = False) -> WorkLogEntry:
        """Log a todo item."""
        entry_type = EntryType.TODO_COMPLETE if complete else EntryType.TODO
        return self.append(entry_type, todo)

    def log_plan(self, plan: str) -> WorkLogEntry:
        """Log the iteration plan."""
        return self.append(EntryType.PLAN, plan)

    def extract_from_output(self, output: str) -> list[WorkLogEntry]:
        """Extract structured entries from agent output.

        Looks for <decision>, <learning> tags and todo patterns.

        Args:
            output: Raw agent output text

        Returns:
            List of entries extracted
        """
        extracted = []

        # Extract decisions
        for match in self.DECISION_PATTERN.finditer(output):
            entry = self.log_decision(match.group(1).strip())
            extracted.append(entry)

        # Extract learnings
        for match in self.LEARNING_PATTERN.finditer(output):
            entry = self.log_learning(match.group(1).strip())
            extracted.append(entry)

        return extracted

    def get_recent_entries(self, n: int = 10) -> list[WorkLogEntry]:
        """Get the most recent entries.

        Args:
            n: Number of entries to return

        Returns:
            List of most recent entries (newest last)
        """
        return self.entries[-n:] if len(self.entries) > n else self.entries

    def get_decisions(self) -> list[WorkLogEntry]:
        """Get all decision entries."""
        return [e for e in self.entries if e.entry_type == EntryType.DECISION]

    def get_learnings(self) -> list[WorkLogEntry]:
        """Get all learning entries."""
        return [e for e in self.entries if e.entry_type == EntryType.LEARNING]

    def get_summary(self) -> str:
        """Get a summary of the worklog for progress.txt.

        Returns:
            Formatted summary string
        """
        decisions = self.get_decisions()
        learnings = self.get_learnings()

        lines = []

        if decisions:
            for d in decisions:
                lines.append(f"📋 Decision: {d.content}")

        if learnings:
            for l in learnings:
                lines.append(f"💡 Learning: {l.content}")

        return "\n".join(lines)

    def finalize(self, success: bool, summary: str = "") -> None:
        """Finalize the worklog with completion status.

        Args:
            success: Whether the iteration succeeded
            summary: Optional summary message
        """
        if not self._initialized:
            return

        status = "Completed successfully" if success else "Failed"
        duration = datetime.now() - self._started

        footer = f"""
---

## Summary

**Status**: {status}
**Duration**: {duration.total_seconds():.1f}s
"""
        if summary:
            footer += f"\n{summary}\n"

        with self.path.open("a") as f:
            f.write(footer)


class WorkLogManager:
    """Manages work logs for a runner session."""

    def __init__(
        self,
        project_path: Path,
        on_entry: Callable[[str, WorkLogEntry], None] | None = None,
    ):
        """Initialize worklog manager.

        Args:
            project_path: Project root directory
            on_entry: Callback for entry notifications (story_id, entry)
        """
        self.project_path = project_path
        self.worklog_dir = project_path / "worklogs"
        self._on_entry = on_entry
        self._active_logs: dict[str, WorkLog] = {}

    def get_or_create(self, story_id: str, story_title: str) -> WorkLog:
        """Get or create a worklog for a story.

        Args:
            story_id: Story identifier
            story_title: Story title

        Returns:
            WorkLog instance for the story
        """
        if story_id not in self._active_logs:
            # Create callback wrapper to include story_id
            def entry_callback(entry: WorkLogEntry) -> None:
                if self._on_entry:
                    self._on_entry(story_id, entry)

            worklog = WorkLog(
                story_id=story_id,
                story_title=story_title,
                worklog_dir=self.worklog_dir,
                on_entry=entry_callback,
            )
            self._active_logs[story_id] = worklog

        return self._active_logs[story_id]

    def finalize_story(self, story_id: str, success: bool, summary: str = "") -> None:
        """Finalize a story's worklog.

        Args:
            story_id: Story identifier
            success: Whether the story completed successfully
            summary: Optional summary message
        """
        if story_id in self._active_logs:
            self._active_logs[story_id].finalize(success, summary)

    def get_active_worklog(self, story_id: str) -> WorkLog | None:
        """Get the active worklog for a story if it exists."""
        return self._active_logs.get(story_id)
