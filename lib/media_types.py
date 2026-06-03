"""Normalized public records for Rafiki's local multimedia suite."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MediaEntry:
    id: str
    kind: str
    collection: str
    root_key: str
    path: str
    relative_path: str = ""
    subject: str = ""
    project: str = ""
    title: str = ""
    prompt: str = ""
    style: str = ""
    negative_prompt: str = ""
    provider: str = ""
    model: str = ""
    source_manifest: str = ""
    source_url: str = ""
    tags: list[str] = field(default_factory=list)
    review_state: str = ""
    lineage: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    indexed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SubjectProfile:
    key: str
    display_name: str
    root_key: str
    trigger_word: str = ""
    prompt_suites: list[str] = field(default_factory=list)
    album_roots: list[str] = field(default_factory=list)
    training_roots: list[str] = field(default_factory=list)
    model_versions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JobRecord:
    id: str
    kind: str
    provider: str
    status: str
    target_output_dir: str
    cost_estimate: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    error: str = ""
    manifest_path: str = ""
    request: dict[str, Any] = field(default_factory=dict)
    provider_response: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StyleProfile:
    name: str
    suffix: str
    root_key: str = ""
    negative_suffix: str = ""
    source: str = ""
    media_types: list[str] = field(default_factory=list)
    reference_assets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VideoEdit:
    id: str
    project: str
    title: str
    root_key: str
    clips: list[dict[str, Any]] = field(default_factory=list)
    audio_path: str = ""
    effects_preset: str = ""
    render_outputs: list[str] = field(default_factory=list)
    source_manifest: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MediaImportResult:
    root_key: str
    root_path: str
    importer: str
    entries: list[MediaEntry] = field(default_factory=list)
    subjects: list[SubjectProfile] = field(default_factory=list)
    styles: list[StyleProfile] = field(default_factory=list)
    video_edits: list[VideoEdit] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_key": self.root_key,
            "root_path": self.root_path,
            "importer": self.importer,
            "entries": [entry.to_dict() for entry in self.entries],
            "subjects": [subject.to_dict() for subject in self.subjects],
            "styles": [style.to_dict() for style in self.styles],
            "video_edits": [edit.to_dict() for edit in self.video_edits],
            "warnings": self.warnings,
            "summary": {
                "entries": len(self.entries),
                "subjects": len(self.subjects),
                "styles": len(self.styles),
                "video_edits": len(self.video_edits),
            },
        }
