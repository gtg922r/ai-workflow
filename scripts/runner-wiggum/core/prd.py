"""PRD (Product Requirements Document) parser and state management."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Story:
    """Represents a single user story in the PRD."""

    id: str
    title: str
    description: str
    acceptance_criteria: list[str] = field(default_factory=list)
    passes: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Story:
        """Create a Story from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            acceptance_criteria=data.get("acceptanceCriteria", []),
            passes=data.get("passes", False),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert Story to a dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "acceptanceCriteria": self.acceptance_criteria,
            "passes": self.passes,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class PRD:
    """Product Requirements Document containing user stories."""

    project_name: str
    branch_name: str
    stories: list[Story]
    metadata: dict[str, Any] = field(default_factory=dict)
    _path: Path | None = field(default=None, repr=False)

    @classmethod
    def load(cls, path: Path | str) -> PRD:
        """Load a PRD from a JSON file."""
        path = Path(path)
        with path.open() as f:
            data = json.load(f)

        stories = [Story.from_dict(s) for s in data.get("userStories", [])]
        prd = cls(
            project_name=data.get("projectName", ""),
            branch_name=data.get("branchName", ""),
            stories=stories,
            metadata=data.get("metadata", {}),
        )
        prd._path = path
        return prd

    def save(self, path: Path | str | None = None) -> None:
        """Save the PRD to a JSON file."""
        save_path = Path(path) if path else self._path
        if not save_path:
            raise ValueError("No path specified for saving PRD")

        data = {
            "projectName": self.project_name,
            "branchName": self.branch_name,
            "userStories": [s.to_dict() for s in self.stories],
        }
        if self.metadata:
            data["metadata"] = self.metadata

        with save_path.open("w") as f:
            json.dump(data, f, indent=2)

    def get_next_incomplete_story(self) -> Story | None:
        """Get the next story that hasn't passed yet."""
        for story in self.stories:
            if not story.passes:
                return story
        return None

    def mark_story_complete(self, story_id: str) -> bool:
        """Mark a story as complete (passes=True)."""
        for story in self.stories:
            if story.id == story_id:
                story.passes = True
                return True
        return False

    def get_story_by_id(self, story_id: str) -> Story | None:
        """Get a story by its ID."""
        for story in self.stories:
            if story.id == story_id:
                return story
        return None

    @property
    def total_stories(self) -> int:
        """Total number of stories."""
        return len(self.stories)

    @property
    def completed_stories(self) -> int:
        """Number of completed stories."""
        return sum(1 for s in self.stories if s.passes)

    @property
    def pending_stories(self) -> int:
        """Number of pending stories."""
        return self.total_stories - self.completed_stories

    @property
    def is_complete(self) -> bool:
        """Check if all stories are complete."""
        return all(s.passes for s in self.stories)

    @property
    def progress_percent(self) -> float:
        """Get completion percentage."""
        if not self.stories:
            return 100.0
        return (self.completed_stories / self.total_stories) * 100

