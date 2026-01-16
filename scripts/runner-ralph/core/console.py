"""Console UI utilities for Runner Ralph.

Provides styled terminal output with timestamps, symbols, box-drawing,
and color-coded messages for a premium CLI experience.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text


class Symbol:
    """Unicode symbols for console output."""

    # State indicators
    RUNNING = "🚀"
    IDLE = "💤"
    PAUSED = "⏸️"
    COMPLETED = "✅"
    ERROR = "❌"

    # Operations
    SUCCESS = "✓"
    FAILURE = "✗"
    PENDING = "⏳"
    INFO = "ℹ️"
    WARNING = "⚠️"

    # Categories
    GIT = "📦"
    AGENT = "🤖"
    STORY = "📋"
    ITERATION = "🔄"
    REVIEW = "🔍"
    TOKEN = "🪙"
    COST = "💰"
    TIME = "⏱️"

    # Progress
    START = "▶"
    STOP = "■"
    ARROW = "→"
    DOT = "•"


class BoxChars:
    """Box-drawing characters for visual grouping."""

    # Single line
    H = "─"  # Horizontal
    V = "│"  # Vertical
    TL = "┌"  # Top-left corner
    TR = "┐"  # Top-right corner
    BL = "└"  # Bottom-left corner
    BR = "┘"  # Bottom-right corner
    LT = "├"  # Left tee
    RT = "┤"  # Right tee
    TT = "┬"  # Top tee
    BT = "┴"  # Bottom tee
    X = "┼"  # Cross

    # Double line (for emphasis)
    DH = "═"
    DV = "║"
    DTL = "╔"
    DTR = "╗"
    DBL = "╚"
    DBR = "╝"


class ConsoleTheme:
    """Color theme for console output - compatible with most terminals."""

    # State colors
    STATE_IDLE = "dim"
    STATE_RUNNING = "green"
    STATE_PAUSED = "yellow"
    STATE_COMPLETED = "blue"
    STATE_ERROR = "red"

    # Message types
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "cyan"
    DIM = "dim"

    # Accent colors
    PRIMARY = "cyan"
    SECONDARY = "magenta"
    ACCENT = "blue"


@dataclass
class ConsoleConfig:
    """Configuration for console output."""

    show_timestamps: bool = True
    timestamp_format: str = "%H:%M:%S"
    box_width: int = 80


class ConsoleUI:
    """Enhanced console output for Runner Ralph.

    Provides styled, timestamped output with box-drawing characters
    and visual grouping for a premium CLI experience.
    """

    def __init__(
        self,
        config: ConsoleConfig | None = None,
        console: Console | None = None,
    ):
        """Initialize the console UI.

        Args:
            config: Optional configuration for output styling
            console: Optional Rich console instance (creates new if not provided)
        """
        self.config = config or ConsoleConfig()
        self.console = console or Console()
        self._section_open = False

    def _timestamp(self) -> str:
        """Get formatted timestamp string."""
        if self.config.show_timestamps:
            return f"[{datetime.now().strftime(self.config.timestamp_format)}]"
        return ""

    def _styled_timestamp(self) -> Text:
        """Get styled timestamp as Rich Text."""
        ts = self._timestamp()
        if ts:
            return Text(f"{ts} ", style="dim")
        return Text("")

    def log(
        self,
        message: str,
        style: str = "",
        symbol: str = "",
        timestamp: bool = True,
    ) -> None:
        """Output a log message with optional styling.

        Args:
            message: The message to output
            style: Rich style string (e.g., "green", "bold red")
            symbol: Optional symbol prefix
            timestamp: Whether to include timestamp
        """
        parts = []

        if timestamp and self.config.show_timestamps:
            parts.append(Text(f"[{datetime.now().strftime(self.config.timestamp_format)}] ", style="dim"))

        if symbol:
            parts.append(Text(f"{symbol} "))

        parts.append(Text(message, style=style))

        output = Text()
        for part in parts:
            output.append_text(part)

        self.console.print(output)

    # === State Messages ===

    def state_change(self, state_name: str, state_value: str) -> None:
        """Output a state change message."""
        symbols = {
            "idle": Symbol.IDLE,
            "running": Symbol.RUNNING,
            "paused": Symbol.PAUSED,
            "completed": Symbol.COMPLETED,
            "error": Symbol.ERROR,
        }
        styles = {
            "idle": ConsoleTheme.STATE_IDLE,
            "running": ConsoleTheme.STATE_RUNNING,
            "paused": ConsoleTheme.STATE_PAUSED,
            "completed": ConsoleTheme.STATE_COMPLETED,
            "error": ConsoleTheme.STATE_ERROR,
        }

        symbol = symbols.get(state_value.lower(), Symbol.DOT)
        style = styles.get(state_value.lower(), "")

        self.log(f"State: {state_value.title()}", style=style, symbol=symbol)

    def success(self, message: str) -> None:
        """Output a success message."""
        self.log(message, style=ConsoleTheme.SUCCESS, symbol=Symbol.SUCCESS)

    def error(self, message: str) -> None:
        """Output an error message."""
        self.log(message, style=ConsoleTheme.ERROR, symbol=Symbol.FAILURE)

    def warning(self, message: str) -> None:
        """Output a warning message."""
        self.log(message, style=ConsoleTheme.WARNING, symbol=Symbol.WARNING)

    def info(self, message: str) -> None:
        """Output an info message."""
        self.log(message, style=ConsoleTheme.INFO, symbol=Symbol.INFO)

    # === Section Boxes ===

    def section_start(self, title: str, style: str = "cyan") -> None:
        """Start a visual section with box drawing.

        Args:
            title: Section title
            style: Color style for the box
        """
        width = self.config.box_width
        # Calculate available space for the border line after title
        ts = self._timestamp()
        ts_width = len(ts) + 1 if ts else 0  # +1 for space after timestamp
        content_width = width - ts_width

        # Top border with title embedded
        title_display = f" {title} "
        left_border = BoxChars.TL + BoxChars.H * 2
        right_padding = content_width - len(left_border) - len(title_display) - 1
        if right_padding < 0:
            right_padding = 1
        right_border = BoxChars.H * right_padding + BoxChars.TR

        header = f"{ts} [{style}]{left_border}{title_display}{right_border}[/]"
        self.console.print(header)
        self._section_open = True

    def section_line(self, content: str, indent: int = 2) -> None:
        """Output a line within a section.

        Args:
            content: Line content
            indent: Indentation level
        """
        ts = self._timestamp()
        prefix = f"{ts} {BoxChars.V}{' ' * indent}"
        self.console.print(f"[dim]{prefix}[/]{content}")

    def section_end(self, style: str = "cyan") -> None:
        """Close a visual section."""
        ts = self._timestamp()
        ts_width = len(ts) + 1 if ts else 0  # +1 for space after timestamp
        content_width = self.config.box_width - ts_width
        border = BoxChars.BL + BoxChars.H * (content_width - 2) + BoxChars.BR
        self.console.print(f"{ts} [{style}]{border}[/]")
        self._section_open = False

    # === Iteration Display ===

    def iteration_header(self, iteration: int, story_title: str | None = None) -> None:
        """Display an iteration header with visual emphasis.

        Args:
            iteration: Iteration number
            story_title: Optional story title
        """
        self.console.print()

        # Build title
        title_parts = [f"Iteration {iteration}"]
        if story_title:
            title_parts.append(f" {Symbol.ARROW} {story_title}")

        title = "".join(title_parts)

        # Calculate content width accounting for timestamp
        ts = self._timestamp()
        ts_width = len(ts) + 1 if ts else 0  # +1 for space after timestamp
        content_width = self.config.box_width - ts_width

        # Top border (double line for emphasis)
        top = f"{BoxChars.DTL}{BoxChars.DH * (content_width - 2)}{BoxChars.DTR}"
        self.console.print(f"{ts} [cyan bold]{top}[/]")

        # Title line - account for emoji width (roughly)
        title_display = f"{Symbol.ITERATION} {title}"
        # Emoji characters are typically displayed as 2 characters wide
        visible_title_len = len(title_display) + 1  # +1 for emoji extra width
        padding = content_width - visible_title_len - 4
        if padding < 0:
            padding = 1
        mid = f"{BoxChars.DV} {title_display}{' ' * padding}{BoxChars.DV}"
        self.console.print(f"{ts} [cyan bold]{mid}[/]")

        # Bottom border
        bot = f"{BoxChars.DBL}{BoxChars.DH * (content_width - 2)}{BoxChars.DBR}"
        self.console.print(f"{ts} [cyan bold]{bot}[/]")

    def iteration_summary(
        self,
        success: bool,
        tokens: int | None = None,
        cost: float | None = None,
        summary: str = "",
    ) -> None:
        """Display an iteration summary.

        Args:
            success: Whether iteration succeeded
            tokens: Token count (optional)
            cost: Cost in USD (optional)
            summary: Summary text
        """
        ts = self._timestamp()

        # Status line
        if success:
            self.console.print(f"{ts} [green]{Symbol.SUCCESS} Completed[/]")
        else:
            self.console.print(f"{ts} [red]{Symbol.FAILURE} Failed[/]")

        # Stats (if available)
        if tokens is not None or cost is not None:
            self.section_start("Stats", style="dim")
            if tokens is not None:
                self.section_line(f"{Symbol.TOKEN} Tokens: {tokens:,}", indent=1)
            if cost is not None:
                self.section_line(f"{Symbol.COST} Cost: ${cost:.4f}", indent=1)
            self.section_end(style="dim")

        # Summary
        if summary:
            self.console.print(f"{ts} [dim]{Symbol.ARROW} {summary}[/]")

    # === Git Operations ===

    def git_operation(self, message: str) -> None:
        """Output a git operation message."""
        self.log(message, style="magenta", symbol=Symbol.GIT)

    def git_section_start(self, title: str) -> None:
        """Start a git operations section."""
        self.section_start(f"{Symbol.GIT} Git: {title}", style="magenta")

    # === Agent Output ===

    def agent_output_start(self) -> None:
        """Start agent output section."""
        self.section_start(f"{Symbol.AGENT} Agent Output", style="blue")

    def agent_output_line(self, line: str) -> None:
        """Display a line of agent output."""
        self.section_line(f"[dim]{line}[/]", indent=1)

    def agent_output_end(self) -> None:
        """End agent output section."""
        self.section_end(style="blue")

    def agent_output_truncated(self, shown: int, total: int) -> None:
        """Display truncation notice for agent output."""
        omitted = total - shown
        self.section_line(f"[dim italic]... ({omitted} lines omitted) ...[/]", indent=1)

    # === Header / Banner ===

    def banner(
        self,
        title: str,
        subtitle: str = "",
        agent: str = "",
        iterations: int = 0,
        project: str = "",
        git_enabled: bool = True,
        main_branch: str = "main",
        review_enabled: bool = False,
        version: str | None = None,
        model: str | None = None,
    ) -> None:
        """Display the application banner with configuration.

        Args:
            title: Main title
            subtitle: Subtitle/tagline
            agent: Agent name
            iterations: Max iterations
            project: Project path
            git_enabled: Whether git is enabled
            main_branch: Main branch name
            review_enabled: Whether review phase is enabled
            version: Optional agent version
            model: Optional model name
        """
        self.console.print()

        # Create a table for aligned config display
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Key", style="dim")
        table.add_column("Value", style="cyan")

        table.add_row("Agent:", agent.title())
        if version:
            table.add_row("Version:", version)
        if model:
            table.add_row("Model:", model)
        table.add_row("Iterations:", str(iterations))
        table.add_row("Project:", str(project))
        table.add_row("Git:", "enabled" if git_enabled else "disabled")
        if git_enabled:
            table.add_row("Main branch:", main_branch)
        table.add_row("Review:", "enabled" if review_enabled else "disabled")

        # Title panel
        panel = Panel(
            table,
            title=f"[bold]{title}[/]",
            subtitle=f"[dim]{subtitle}[/]" if subtitle else None,
            border_style="cyan",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    # === Final Summary ===

    def final_summary(
        self,
        iterations: int,
        tokens: int,
        cost: float,
        errors: list[str] | None = None,
        duration_seconds: float | None = None,
    ) -> None:
        """Display the final run summary.

        Args:
            iterations: Total iterations completed
            tokens: Total tokens used
            cost: Total cost
            errors: List of errors (optional)
            duration_seconds: Total duration (optional)
        """
        self.console.print()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold")
        table.add_column("Value")

        table.add_row("Iterations:", str(iterations))
        table.add_row("Tokens:", f"{tokens:,}")
        table.add_row("Cost:", f"${cost:.4f}")

        if duration_seconds is not None:
            mins, secs = divmod(int(duration_seconds), 60)
            if mins > 0:
                table.add_row("Duration:", f"{mins}m {secs}s")
            else:
                table.add_row("Duration:", f"{secs}s")

        if errors:
            table.add_row("Errors:", f"[red]{len(errors)}[/]")

        panel = Panel(
            table,
            title=f"[bold]{Symbol.COMPLETED} Run Complete[/]",
            border_style="green" if not errors else "yellow",
            padding=(1, 2),
        )
        self.console.print(panel)

        # Show errors if any
        if errors:
            self.console.print()
            self.section_start(f"{Symbol.ERROR} Errors", style="red")
            for err in errors:
                self.section_line(f"[red]{Symbol.DOT} {err}[/]", indent=1)
            self.section_end(style="red")

    # === Prompts and Warnings ===

    def dirty_warning(self, status: str) -> None:
        """Display warning about dirty working directory.

        Args:
            status: Git status output
        """
        self.console.print()
        self.warning("Working directory has uncommitted changes:")
        self.console.print()

        # Show status in a box
        self.section_start("Git Status", style="yellow")
        for line in status.strip().split("\n"):
            self.section_line(f"[dim]{line}[/]", indent=1)
        self.section_end(style="yellow")

        self.console.print()
        self.console.print("[dim]Git management requires a clean working directory to create branches and commits.[/]")
        self.console.print("[dim]You can either abort and commit/stash your changes, or disable git for this run.[/]")
        self.console.print()

    def reset_prompt(self, message: str) -> None:
        """Display reset prompt message."""
        self.console.print()
        self.warning(message)
        self.console.print()

    # === Utility ===

    def blank_line(self) -> None:
        """Output a blank line."""
        self.console.print()

    def separator(self, style: str = "dim") -> None:
        """Output a horizontal separator."""
        ts = self._timestamp()
        line = BoxChars.H * (self.config.box_width - len(ts) - 1)
        self.console.print(f"{ts} [{style}]{line}[/]")

    def worklog_entry(self, formatted_line: str) -> None:
        """Display a worklog entry."""
        ts = self._timestamp()
        self.console.print(f"{ts} [dim]{formatted_line}[/]")


# Factory function for easy creation
def create_console_ui(
    show_timestamps: bool = True,
    box_width: int = 80,
) -> ConsoleUI:
    """Create a configured ConsoleUI instance.

    Args:
        show_timestamps: Whether to show timestamps on messages
        box_width: Width of box drawings

    Returns:
        Configured ConsoleUI instance
    """
    config = ConsoleConfig(
        show_timestamps=show_timestamps,
        box_width=box_width,
    )
    return ConsoleUI(config=config)
