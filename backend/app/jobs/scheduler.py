from __future__ import annotations

import os
import threading
import time

from app.ingestion.legistar_ingest import run_legistar_ingest


def run_once() -> dict[str, int]:
    result = run_legistar_ingest(mode='incremental', source='whatcom_legistar_api')
    return result.__dict__


def start_background_scheduler() -> None:
    interval = int(os.getenv('INGEST_INTERVAL_SECONDS', '1800'))

    def _loop() -> None:
        while True:
            try:
                run_once()
            except Exception:
                pass
            time.sleep(max(1800, min(interval, 3600)))

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
