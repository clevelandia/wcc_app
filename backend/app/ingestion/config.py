from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ExtractionHints(BaseModel):
    mode: Literal["api", "html", "rss", "gis"]
    parser: str
    table_aware: bool = False


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    kind: Literal["legistar", "rss", "gis", "zoning", "zotero"]
    enabled: bool = True
    cadence: str = Field(description="cron-like cadence")
    provenance: str
    base_url: HttpUrl
    extraction_hints: ExtractionHints


class SourcesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources: list[SourceConfig]


def load_sources_config(path: str | Path) -> SourcesConfig:
    raw = yaml.safe_load(Path(path).read_text())
    return SourcesConfig.model_validate(raw)
