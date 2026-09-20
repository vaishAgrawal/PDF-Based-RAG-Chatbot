"""FAISS-backed vector storage."""

import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(self, directory: str | Path, embedder) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self.index = None
        self.documents: list[str] = []
        self._load()

    def add(self, documents: list[str]) -> None:
        if not documents:
            return
        vectors = np.asarray(self.embedder.encode(documents), dtype="float32")
        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.documents.extend(documents)
        self._save()

    def search(self, query: str, limit: int = 4) -> list[str]:
        if self.index is None or not self.documents:
            return []
        vector = np.asarray(self.embedder.encode([query]), dtype="float32")
        _, indices = self.index.search(vector, min(limit, len(self.documents)))
        return [self.documents[index] for index in indices[0] if index >= 0]

    def _save(self) -> None:
        faiss.write_index(self.index, str(self.directory / "index.faiss"))
        (self.directory / "documents.json").write_text(
            json.dumps(self.documents, ensure_ascii=False), encoding="utf-8"
        )

    def _load(self) -> None:
        index_path = self.directory / "index.faiss"
        documents_path = self.directory / "documents.json"
        if index_path.exists() and documents_path.exists():
            self.index = faiss.read_index(str(index_path))
            self.documents = json.loads(documents_path.read_text(encoding="utf-8"))
