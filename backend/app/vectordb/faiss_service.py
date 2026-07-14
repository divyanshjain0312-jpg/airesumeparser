"""FAISS-backed vector store, one index per session.

Because embedders normalize vectors, we use IndexFlatIP so inner product
equals cosine similarity. Sessions are cached in memory and can also be
persisted to disk (see save/load helpers).
"""
from __future__ import annotations

import pickle
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np


class FAISSStore:
    """A single FAISS index + chunk-text lookup for one session."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: List[str] = []

    def add(self, embeddings: np.ndarray, chunks: List[str]) -> None:
        if embeddings.shape[0] != len(chunks):
            raise ValueError("embeddings and chunks must have the same length")
        if embeddings.shape[0] == 0:
            return
        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"embedding dim mismatch: got {embeddings.shape[1]}, expected {self.dimension}"
            )
        self.index.add(embeddings.astype(np.float32))
        self.chunks.extend(chunks)

    def search(self, query_vec: np.ndarray, top_k: int) -> List[Tuple[int, float, str]]:
        if self.index.ntotal == 0:
            return []
        k = min(top_k, self.index.ntotal)
        query = query_vec.reshape(1, -1).astype(np.float32)
        scores, indices = self.index.search(query, k)
        results: List[Tuple[int, float, str]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            results.append((int(idx), float(score), self.chunks[int(idx)]))
        return results

    def size(self) -> int:
        return self.index.ntotal

    # ---- persistence (optional; used if you want to keep sessions on disk) ----

    def save(self, dir_path: Path) -> None:
        dir_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(dir_path / "index.faiss"))
        with (dir_path / "chunks.pkl").open("wb") as f:
            pickle.dump({"dimension": self.dimension, "chunks": self.chunks}, f)

    @classmethod
    def load(cls, dir_path: Path) -> "FAISSStore":
        with (dir_path / "chunks.pkl").open("rb") as f:
            meta = pickle.load(f)
        store = cls(dimension=int(meta["dimension"]))
        store.index = faiss.read_index(str(dir_path / "index.faiss"))
        store.chunks = list(meta["chunks"])
        return store


class FAISSSessionManager:
    """In-memory registry of FAISSStore keyed by session id."""

    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._sessions: Dict[str, FAISSStore] = {}
        self._lock = threading.Lock()

    def create(self, session_id: str, dimension: int) -> FAISSStore:
        with self._lock:
            store = FAISSStore(dimension=dimension)
            self._sessions[session_id] = store
            return store

    def get(self, session_id: str) -> Optional[FAISSStore]:
        with self._lock:
            store = self._sessions.get(session_id)
        if store is not None:
            return store
        # Try loading from disk
        disk_path = self._root / session_id
        if (disk_path / "index.faiss").exists():
            store = FAISSStore.load(disk_path)
            with self._lock:
                self._sessions[session_id] = store
            return store
        return None

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def save_to_disk(self, session_id: str) -> None:
        store = self.get(session_id)
        if store is None:
            return
        store.save(self._root / session_id)


_manager_singleton: Optional[FAISSSessionManager] = None
_manager_lock = threading.Lock()


def get_session_manager(root_dir: Path) -> FAISSSessionManager:
    global _manager_singleton
    with _manager_lock:
        if _manager_singleton is None:
            _manager_singleton = FAISSSessionManager(root_dir)
        return _manager_singleton
