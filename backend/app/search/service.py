from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchDoc:
    id: str
    text: str
    metadata: dict


@dataclass
class SearchService:
    docs: list[SearchDoc] = field(default_factory=list)

    def index(self, doc: SearchDoc) -> None:
        self.docs.append(doc)

    def fts(self, query: str) -> list[SearchDoc]:
        q = query.lower()
        return [d for d in self.docs if q in d.text.lower()]

    def semantic(self, query: str) -> list[SearchDoc]:
        terms = set(query.lower().split())
        return sorted(self.docs, key=lambda d: -len(terms.intersection(set(d.text.lower().split()))))[:10]
