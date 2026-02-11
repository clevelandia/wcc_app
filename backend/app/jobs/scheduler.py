from __future__ import annotations

from app.ingestion.adapters.gis import GISAdapter
from app.ingestion.adapters.legistar_api import LegistarAPIAdapter
from app.ingestion.adapters.rss import RSSAdapter
from app.ingestion.pipeline import IngestionPipeline


def run_once() -> dict[str, dict[str, int]]:
    pipeline = IngestionPipeline()
    adapters = {
        "legistar_api": LegistarAPIAdapter("https://webapi.legistar.com/v1/whatcomwa/events"),
        "rss": RSSAdapter("https://www.cascadiadaily.com/feed", "Cascadia Daily News"),
        "gis": GISAdapter("https://services.arcgis.com/example", "tax_parcel"),
    }
    return {name: pipeline.run_adapter(adapter) for name, adapter in adapters.items()}
