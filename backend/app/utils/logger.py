"""Lightweight in-memory logger that collects timestamped events.

Each RAG pipeline call gets its own DebugLogger; the collected lines are
returned in the API response so the frontend can render them in the
"Debug Logs" accordion.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import List

_pylog = logging.getLogger("rag")


class DebugLogger:
    def __init__(self) -> None:
        self._lines: List[str] = []
        self._start = time.perf_counter()

    def log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}"
        self._lines.append(line)
        _pylog.info(message)

    def error(self, message: str) -> None:
        self.log(f"ERROR: {message}")

    @property
    def lines(self) -> List[str]:
        return list(self._lines)

    @property
    def elapsed_seconds(self) -> float:
        return round(time.perf_counter() - self._start, 3)
