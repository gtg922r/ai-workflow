#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "textual>=0.47.0",
#     "rich>=13.0.0",
# ]
# ///
"""Runner Ralph - Autonomous AI Agent Runner.

A CLI application for running autonomous AI agent loops.

Usage:
    # Console mode (default)
    uv run scripts/runner-ralph/ralph.py
    uv run scripts/runner-ralph/ralph.py --agent cursor --iterations 3

    # Specify a model
    uv run scripts/runner-ralph/ralph.py --agent claude --model claude-sonnet-4-20250514

    # Interactive TUI mode
    uv run scripts/runner-ralph/ralph.py --tui
    uv run scripts/runner-ralph/ralph.py --tui --path /path/to/project
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure local packages (agents/, core/) are importable when run from anywhere
_script_dir = Path(__file__).parent.resolve()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

import asyncio

from agents.base import AgentResult, AgentType
from core.controller import RunnerCallbacks, RunnerController
from core.prd import PRD, Story
from core.runner import RunnerConfig, RunnerState
from core.worklog import WorkLogEntry


# =============================================================================
# Console Mode (no TUI) - Enhanced console runner with premium CLI feel
# =============================================================================


class ConsoleRunner:
    """Enhanced console-based runner with polished UI output.

    Features:
    - Timestamped log entries [HH:MM:SS] (optional)
    - Unicode symbols for state changes and results
    - Box-drawing characters for visual grouping
    - Improved layout for summaries and error messages
    """

    def __init__(
        self,
        project_path: Path,
        config: RunnerConfig,
        verbose: bool = False,
        show_timestamps: bool = False,
    ):
        self.project_path = project_path
        self.config = config
        self.controller = RunnerController(project_path)
        self.verbose = verbose

        # Initialize the enhanced console UI
        from core.console import create_console_ui

        # Enable timestamps if explicitly requested or in verbose mode
        timestamps = show_timestamps or verbose
        self.ui = create_console_ui(show_timestamps=timestamps, box_width=80)

    def _on_state_change(self, state: RunnerState) -> None:
        """Handle state change with styled output."""
        self.ui.state_change("State", state.value)

    def _on_git_dirty(self, status: str) -> bool:
        """Handle dirty working directory - prompt user.

        Returns True to disable git and continue, False to abort.
        """
        from rich.prompt import Confirm

        self.ui.dirty_warning(status)
        return Confirm.ask("Disable git management and continue?", default=False)

    def _on_git_reset_prompt(self, message: str) -> bool:
        """Handle failure reset prompt."""
        from rich.prompt import Confirm

        self.ui.reset_prompt(message)
        return Confirm.ask("Reset branch and discard changes?", default=False)

    def _on_iteration_start(self, iteration: int, story: Story | None) -> None:
        """Handle iteration start with visual header."""
        story_title = story.title if story else None
        self.ui.iteration_header(iteration, story_title)

    def _on_iteration_end(self, iteration: int, result: AgentResult) -> None:
        """Handle iteration end with structured summary."""
        from core.console import Symbol

        # Show success/failure status
        if result.success:
            self.ui.success("Completed")
        else:
            self.ui.error(f"Failure: {result.error or 'unknown error'}")

        # Show output in a visual box (if there's substantial output)
        if result.output and result.output.strip():
            lines = result.output.strip().split("\n")
            self.ui.agent_output_start()

            if len(lines) > 50:
                # Show first 25 lines
                for line in lines[:25]:
                    self.ui.agent_output_line(line)
                # Truncation notice
                self.ui.agent_output_truncated(50, len(lines))
                # Show last 25 lines
                for line in lines[-25:]:
                    self.ui.agent_output_line(line)
            else:
                for line in lines:
                    self.ui.agent_output_line(line)

            self.ui.agent_output_end()

        # Show iteration summary
        self.ui.iteration_summary(
            success=result.success,
            tokens=result.tokens_used,
            cost=result.cost,
            summary=result.summary,
        )

    def _on_output(self, text: str) -> None:
        """Handle general output messages."""
        # Check if it's a git message (prefixed with [git])
        if text.startswith("[git]"):
            # Git messages already have symbols, just format nicely
            git_msg = text[5:].strip()
            self.ui.log(git_msg, style="magenta", timestamp=True)
        else:
            self.ui.info(text)

    def _on_worklog_entry(self, story_id: str, entry: WorkLogEntry) -> None:
        """Handle worklog entry updates - display with formatting."""
        self.ui.worklog_entry(entry.format_line())

    async def run(self) -> None:
        """Run in console mode with enhanced UI."""
        from agents.base import AgentConfig
        from agents.registry import create_agent

        # Check agent availability first
        agent_config = AgentConfig(
            working_dir=self.project_path,
            timeout_seconds=self.config.timeout_seconds,
        )
        agent = create_agent(self.config.agent_type, agent_config)

        if not agent.is_available():
            self.ui.error(f"{self.config.agent_type.value} agent is not available!")
            if self.config.agent_type == AgentType.CURSOR:
                self.ui.warning("Install Cursor CLI with: curl https://cursor.com/install -fsS | bash")
            return

        version = agent.get_version()

        # Display banner with configuration
        self.ui.banner(
            title="Runner Ralph",
            subtitle="Autonomous Agent Runner - Console Mode",
            agent=self.config.agent_type.value,
            iterations=self.config.max_iterations,
            project=str(self.project_path),
            git_enabled=self.config.git_enabled,
            main_branch=self.config.main_branch,
            review_enabled=self.config.review_enabled,
            version=version,
            model=self.config.model,
        )

        if self.verbose:
            self.ui.info("Verbose mode enabled")

        # Set up callbacks
        self.controller.set_callbacks(
            RunnerCallbacks(
                on_state_change=self._on_state_change,
                on_iteration_start=self._on_iteration_start,
                on_iteration_end=self._on_iteration_end,
                on_output=self._on_output,
                on_git_dirty=self._on_git_dirty,
                on_git_reset_prompt=self._on_git_reset_prompt,
                on_worklog_entry=self._on_worklog_entry,
            )
        )

        self.controller.configure(self.config)

        # Run with graceful interrupt handling
        start_time = None
        try:
            from datetime import datetime
            start_time = datetime.now()
            await self.controller.run()
        except KeyboardInterrupt:
            self.ui.blank_line()
            self.ui.warning("Interrupted by user")
            self.controller.stop()
        except Exception as e:
            self.ui.blank_line()
            self.ui.error(f"Error: {e}")
            raise

        # Calculate duration
        duration_seconds = None
        if start_time:
            from datetime import datetime
            duration_seconds = (datetime.now() - start_time).total_seconds()

        # Display final summary
        if self.controller.runner:
            stats = self.controller.runner.stats
            self.ui.final_summary(
                iterations=stats.iterations_completed,
                tokens=stats.total_tokens,
                cost=stats.total_cost,
                errors=stats.errors if stats.errors else None,
                duration_seconds=duration_seconds,
            )


def run_console_mode(
    project_path: Path,
    agent_type: AgentType,
    max_iterations: int,
    timeout: int,
    verbose: bool = False,
    show_timestamps: bool = False,
    git_enabled: bool = True,
    main_branch: str = "main",
    use_main_as_base: bool = False,
    review_enabled: bool = False,
    model: str | None = None,
) -> None:
    """Run the agent in simple console mode (no TUI)."""
    config = RunnerConfig(
        project_path=project_path,
        agent_type=agent_type,
        max_iterations=max_iterations,
        timeout_seconds=timeout,
        allow_network=True,
        git_enabled=git_enabled,
        main_branch=main_branch,
        use_main_as_base=use_main_as_base,
        review_enabled=review_enabled,
        model=model,
    )

    runner = ConsoleRunner(
        project_path, config, verbose=verbose, show_timestamps=show_timestamps
    )
    asyncio.run(runner.run())


# =============================================================================
# TUI Mode - Full terminal UI
# =============================================================================


# Import TUI deps at module level for TUI mode
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Log,
    ProgressBar,
    RadioButton,
    RadioSet,
    Rule,
    Static,
    Switch,
)


class ConfigScreen(ModalScreen[RunnerConfig | None]):
    """Configuration screen for setting up the runner."""

    CSS = """
    ConfigScreen {
        align: center middle;
    }

    #config-dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #config-dialog Label {
        margin-top: 1;
    }

    #config-dialog Input {
        margin-bottom: 1;
    }

    #config-dialog .buttons {
        margin-top: 2;
        align: center middle;
    }

    #config-dialog Button {
        margin: 0 1;
    }

    .agent-option {
        padding: 0 1;
    }

    .agent-unavailable {
        color: $text-muted;
    }
    """

    def __init__(
        self,
        project_path: Path,
        available_agents: list[tuple[AgentType, bool, str | None]],
    ):
        super().__init__()
        self.project_path = project_path
        self.available_agents = available_agents

    def compose(self) -> ComposeResult:
        with Container(id="config-dialog"):
            yield Label("⚙️  Runner Ralph Configuration", classes="title")
            yield Rule()

            yield Label("Select Agent:")
            with RadioSet(id="agent-select"):
                for agent_type, available, version in self.available_agents:
                    label = f"{agent_type.value.title()}"
                    if version:
                        label += f" ({version})"
                    if not available:
                        label += " [unavailable]"

                    yield RadioButton(
                        label,
                        value=available,
                        disabled=not available,
                        id=f"agent-{agent_type.value}",
                    )

            yield Label("Max Iterations:")
            yield Input(
                value="10",
                placeholder="Number of iterations",
                id="max-iterations",
                type="integer",
            )

            yield Label("Timeout (seconds):")
            yield Input(
                value="600",
                placeholder="Timeout per iteration",
                id="timeout",
                type="integer",
            )

            with Horizontal():
                yield Label("Allow Network Access:")
                yield Switch(value=True, id="allow-network")

            with Horizontal():
                yield Label("Auto-restart on completion:")
                yield Switch(value=False, id="auto-restart")

            with Horizontal():
                yield Label("Enable Review Phase:")
                yield Switch(value=False, id="review-enabled")

            with Horizontal(classes="buttons"):
                yield Button("Start", variant="primary", id="config-start-btn")
                yield Button("Cancel", variant="default", id="config-cancel-btn")

    @on(Button.Pressed, "#config-start-btn")
    def handle_start(self) -> None:
        """Handle start button press."""
        # Get selected agent
        agent_type = AgentType.CLAUDE  # Default
        radio_set = self.query_one("#agent-select", RadioSet)
        if radio_set.pressed_button:
            button_id = radio_set.pressed_button.id or ""
            if "cursor" in button_id:
                agent_type = AgentType.CURSOR

        # Get other settings
        max_iter_input = self.query_one("#max-iterations", Input)
        timeout_input = self.query_one("#timeout", Input)
        network_switch = self.query_one("#allow-network", Switch)
        restart_switch = self.query_one("#auto-restart", Switch)
        review_switch = self.query_one("#review-enabled", Switch)

        try:
            max_iterations = int(max_iter_input.value or "10")
        except ValueError:
            max_iterations = 10

        try:
            timeout = int(timeout_input.value or "600")
        except ValueError:
            timeout = 600

        config = RunnerConfig(
            project_path=self.project_path,
            agent_type=agent_type,
            max_iterations=max_iterations,
            timeout_seconds=timeout,
            allow_network=network_switch.value,
            auto_restart=restart_switch.value,
            review_enabled=review_switch.value,
        )

        self.dismiss(config)

    @on(Button.Pressed, "#config-cancel-btn")
    def handle_cancel(self) -> None:
        """Handle cancel button press."""
        self.dismiss(None)


class RunHistoryItem(Static):
    """Widget for displaying a run history item."""

    def __init__(self, iteration: int, result: AgentResult, story: Story | None):
        super().__init__()
        self.iteration = iteration
        self.result = result
        self.story = story

    def compose(self) -> ComposeResult:
        status = "✓" if self.result.success else "✗"
        story_id = f"[{self.story.id}]" if self.story else ""

        summary = self.result.summary[:60] + "..." if len(self.result.summary) > 60 else self.result.summary

        text = Text()
        text.append(f"{status} ", style="green" if self.result.success else "red")
        text.append(f"#{self.iteration} ", style="bold")
        text.append(f"{story_id} ", style="cyan")
        text.append(summary, style="dim")

        if self.result.tokens_used:
            text.append(f" ({self.result.tokens_used:,} tokens)", style="dim")

        yield Static(text)


class RalphApp(App):
    """Main Runner Ralph TUI application."""

    TITLE = "Runner Ralph"
    SUB_TITLE = "Autonomous Agent Runner"

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
    }

    #sidebar {
        width: 30;
        border-right: solid $primary;
        padding: 1;
    }

    #content {
        width: 1fr;
        padding: 1;
    }

    #stats-panel {
        height: auto;
        border: round $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #prd-panel {
        height: auto;
        max-height: 15;
        border: round $secondary;
        padding: 1;
        margin-bottom: 1;
    }

    #controls {
        height: auto;
        padding: 1;
    }

    #controls Button {
        margin: 0 1 1 0;
    }

    #output-log {
        height: 1fr;
        border: round $accent;
    }

    #history-panel {
        height: 15;
        border: round $warning;
        margin-top: 1;
    }

    .panel-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    .stat-row {
        margin: 0;
    }

    .stat-label {
        width: 15;
        color: $text-muted;
    }

    .stat-value {
        color: $text;
    }

    ProgressBar {
        margin: 1 0;
    }

    #state-indicator {
        text-style: bold;
        padding: 0 1;
    }

    .state-idle { color: $text-muted; }
    .state-running { color: $success; }
    .state-paused { color: $warning; }
    .state-completed { color: $primary; }
    .state-error { color: $error; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "start", "Start"),
        Binding("p", "pause", "Pause"),
        Binding("r", "restart", "Restart"),
        Binding("c", "configure", "Configure"),
    ]

    def __init__(self, project_path: Path | None = None):
        super().__init__()
        self.project_path = project_path or Path.cwd()
        self.controller = RunnerController(self.project_path)
        self.config: RunnerConfig | None = None
        self._run_task: asyncio.Task | None = None
        self._current_story: Story | None = None
        self._history: list[tuple[int, AgentResult, Story | None]] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                # Stats panel
                with Container(id="stats-panel"):
                    yield Static("📊 Session Stats", classes="panel-title")
                    with Horizontal(classes="stat-row"):
                        yield Static("State:", classes="stat-label")
                        yield Static("Idle", id="state-indicator", classes="state-idle")
                    with Horizontal(classes="stat-row"):
                        yield Static("Agent:", classes="stat-label")
                        yield Static("-", id="agent-name", classes="stat-value")
                    with Horizontal(classes="stat-row"):
                        yield Static("Iterations:", classes="stat-label")
                        yield Static("0 / 0", id="iterations", classes="stat-value")
                    with Horizontal(classes="stat-row"):
                        yield Static("Tokens:", classes="stat-label")
                        yield Static("0", id="total-tokens", classes="stat-value")
                    with Horizontal(classes="stat-row"):
                        yield Static("Cost:", classes="stat-label")
                        yield Static("$0.00", id="total-cost", classes="stat-value")

                # PRD Status panel
                with Container(id="prd-panel"):
                    yield Static("📋 PRD Status", classes="panel-title")
                    yield Static("No PRD loaded", id="prd-status")
                    yield ProgressBar(total=100, show_eta=False, id="prd-progress")

                # Control buttons
                with Container(id="controls"):
                    yield Button("▶ Start", variant="success", id="start-btn")
                    yield Button("⏸ Pause", variant="warning", id="pause-btn", disabled=True)
                    yield Button("🔄 Restart", variant="default", id="restart-btn", disabled=True)
                    yield Button("⚙ Config", variant="primary", id="config-btn")

            with Vertical(id="content"):
                yield Static("📝 Agent Output", classes="panel-title")
                yield Log(id="output-log", highlight=True)

                with VerticalScroll(id="history-panel"):
                    yield Static("📜 Run History", classes="panel-title")
                    yield Container(id="history-list")

        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount."""
        self._update_prd_display()

    def _update_prd_display(self) -> None:
        """Update the PRD status display."""
        prd_path = self.project_path / "prd.json"
        prd_status = self.query_one("#prd-status", Static)
        prd_progress = self.query_one("#prd-progress", ProgressBar)

        if prd_path.exists():
            try:
                prd = PRD.load(prd_path)
                prd_status.update(
                    f"{prd.project_name}\n"
                    f"{prd.completed_stories}/{prd.total_stories} stories"
                )
                prd_progress.update(progress=prd.progress_percent)
            except Exception as e:
                prd_status.update(f"Error loading PRD: {e}")
        else:
            prd_status.update("No prd.json found")

    def _update_state_display(self, state: RunnerState) -> None:
        """Update the state indicator."""
        indicator = self.query_one("#state-indicator", Static)
        indicator.update(state.value.title())

        # Remove old state classes
        for cls in ["state-idle", "state-running", "state-paused", "state-completed", "state-error"]:
            indicator.remove_class(cls)

        # Add new state class
        indicator.add_class(f"state-{state.value}")

        # Update button states
        start_btn = self.query_one("#start-btn", Button)
        pause_btn = self.query_one("#pause-btn", Button)
        restart_btn = self.query_one("#restart-btn", Button)

        if state == RunnerState.RUNNING:
            start_btn.disabled = True
            pause_btn.disabled = False
            restart_btn.disabled = True
        elif state in (RunnerState.PAUSED, RunnerState.COMPLETED, RunnerState.ERROR):
            start_btn.disabled = True
            pause_btn.disabled = True
            restart_btn.disabled = False
        else:
            start_btn.disabled = False
            pause_btn.disabled = True
            restart_btn.disabled = True

    def _update_stats_display(self) -> None:
        """Update the stats display."""
        if not self.controller.runner:
            return

        stats = self.controller.runner.stats

        iterations = self.query_one("#iterations", Static)
        iterations.update(f"{stats.iterations_completed} / {self.config.max_iterations if self.config else 0}")

        tokens = self.query_one("#total-tokens", Static)
        tokens.update(f"{stats.total_tokens:,}")

        cost = self.query_one("#total-cost", Static)
        cost.update(f"${stats.total_cost:.4f}")

    def _on_runner_state_change(self, state: RunnerState) -> None:
        """Handle runner state changes."""
        # Called from async worker (same thread), so call directly
        self._update_state_display(state)

    def _on_iteration_start(self, iteration: int, story: Story | None) -> None:
        """Handle iteration start."""
        self._current_story = story
        log = self.query_one("#output-log", Log)
        story_info = f" - {story.title}" if story else ""
        log.write_line(f"\n{'='*50}")
        log.write_line(f"[bold cyan]Iteration {iteration}{story_info}[/]")
        log.write_line(f"{'='*50}")

    def _on_iteration_end(self, iteration: int, result: AgentResult) -> None:
        """Handle iteration end."""
        log = self.query_one("#output-log", Log)

        if result.success:
            log.write_line("[green]✓ Completed[/]")
        else:
            log.write_line(f"[red]✗ Failed: {result.error or 'Unknown error'}[/]")

        if result.tokens_used:
            log.write_line(f"[dim]Tokens: {result.tokens_used:,}[/]")
        if result.cost:
            log.write_line(f"[dim]Cost: ${result.cost:.4f}[/]")

        # Add to history
        self._history.append((iteration, result, self._current_story))
        self._update_history_display()
        self._update_stats_display()
        self._update_prd_display()

    def _on_output(self, text: str) -> None:
        """Handle output from runner."""
        log = self.query_one("#output-log", Log)
        log.write_line(text)

    def _on_worklog_entry(self, story_id: str, entry: WorkLogEntry) -> None:
        """Handle worklog entry updates - display in log panel."""
        log = self.query_one("#output-log", Log)
        log.write_line(f"[dim]{entry.format_line()}[/]")

    def _update_history_display(self) -> None:
        """Update the run history display."""
        history_list = self.query_one("#history-list", Container)
        history_list.remove_children()

        # Show last 10 runs in reverse order
        for iteration, result, story in reversed(self._history[-10:]):
            history_list.mount(RunHistoryItem(iteration, result, story))

    async def _run_agent(self) -> None:
        """Run the agent loop."""
        await self.controller.run()

    @work(exclusive=True)
    async def _show_config_and_start(self) -> None:
        """Worker method to show config screen and start the agent."""
        # Get available agents
        available_agents = self.controller.get_available_agents()

        # Show config screen
        config = await self.push_screen_wait(
            ConfigScreen(self.project_path, available_agents)
        )

        if not config:
            return

        self.config = config

        # Update agent name display
        agent_name = self.query_one("#agent-name", Static)
        agent_name.update(config.agent_type.value.title())

        # Create and start runner
        self.controller.set_callbacks(
            RunnerCallbacks(
                on_state_change=self._on_runner_state_change,
                on_iteration_start=self._on_iteration_start,
                on_iteration_end=self._on_iteration_end,
                on_output=self._on_output,
                on_worklog_entry=self._on_worklog_entry,
            )
        )
        self.controller.configure(config)
        self._history.clear()
        self._update_history_display()

        log = self.query_one("#output-log", Log)
        log.clear()
        log.write_line("[bold]Starting Runner Ralph...[/]")

        # Run agent loop (worker handles threading)
        await self._run_agent()

    @on(Button.Pressed, "#start-btn")
    def action_start(self) -> None:
        """Start the agent runner (triggered by button or 's' key)."""
        self._show_config_and_start()

    @on(Button.Pressed, "#pause-btn")
    def action_pause(self) -> None:
        """Pause the agent runner."""
        if self.controller.runner:
            self.controller.stop()
            log = self.query_one("#output-log", Log)
            log.write_line("[yellow]Pause requested...[/]")

    @work(exclusive=True)
    async def _restart_agent(self) -> None:
        """Worker method to restart the agent."""
        if self.controller.runner:
            self.controller.reset()
            self._history.clear()
            self._update_history_display()

            log = self.query_one("#output-log", Log)
            log.clear()
            log.write_line("[bold]Restarting Runner Ralph...[/]")

            await self._run_agent()

    @on(Button.Pressed, "#restart-btn")
    def action_restart(self) -> None:
        """Restart the agent runner (triggered by button or 'r' key)."""
        self._restart_agent()

    @work(exclusive=True)
    async def _show_config_only(self) -> None:
        """Worker method to show config screen for settings only."""
        # Get available agents
        available_agents = self.controller.get_available_agents()

        config = await self.push_screen_wait(
            ConfigScreen(self.project_path, available_agents)
        )

        if config:
            self.config = config
            agent_name = self.query_one("#agent-name", Static)
            agent_name.update(config.agent_type.value.title())

    @on(Button.Pressed, "#config-btn")
    def action_configure(self) -> None:
        """Open configuration screen (triggered by button or 'c' key)."""
        self._show_config_only()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Runner Ralph - Autonomous AI Agent Runner"
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        default=Path.cwd(),
        help="Project path (default: current directory)",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Run in interactive TUI mode",
    )
    parser.add_argument(
        "--agent",
        "-a",
        type=str,
        choices=["cursor", "claude"],
        default="cursor",
        help="Agent to use (default: cursor)",
    )
    parser.add_argument(
        "--iterations",
        "-n",
        type=int,
        default=3,
        help="Max iterations (default: 3)",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=600,
        help="Timeout per iteration in seconds (default: 600)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output including full agent responses",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Show timestamps in console output",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Disable git state management (branch creation, commits, etc.)",
    )
    parser.add_argument(
        "--main-branch",
        type=str,
        default="main",
        help="Name of the main branch, used with --use-main (default: main)",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Enable post-implementation review phase (reviewer critiques code before merging)",
    )
    parser.add_argument(
        "--use-main",
        action="store_true",
        help="Always branch from main (default: use current branch as base for story branches)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=None,
        help="Model to use (e.g., claude-sonnet-4-20250514, gpt-4o). Passed to agent CLI --model flag.",
    )
    args = parser.parse_args()

    project_path = args.path.resolve()

    if args.tui:
        # Full TUI mode
        app = RalphApp(project_path=project_path)
        app.run()
    else:
        # Console mode (default)
        agent_type = AgentType.CURSOR if args.agent == "cursor" else AgentType.CLAUDE
        run_console_mode(
            project_path=project_path,
            agent_type=agent_type,
            max_iterations=args.iterations,
            timeout=args.timeout,
            verbose=args.verbose,
            show_timestamps=args.timestamps,
            git_enabled=not args.no_git,
            main_branch=args.main_branch,
            use_main_as_base=args.use_main,
            review_enabled=args.review,
            model=args.model,
        )


if __name__ == "__main__":
    main()

