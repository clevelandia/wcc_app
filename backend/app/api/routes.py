from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.analysis.budget_delta import budget_delta
from app.analysis.semantic_diff import semantic_diff
from app.ragg.briefs import generate_organizer_brief
from app.search.service import SearchDoc, SearchService

router = APIRouter()
search_service = SearchService()


class SearchRequest(BaseModel):
    query: str


class BudgetDiffRequest(BaseModel):
    old_rows: list[dict]
    new_rows: list[dict]


class SemanticDiffRequest(BaseModel):
    old_sections: dict[str, str]
    new_sections: dict[str, str]


class BriefRequest(BaseModel):
    topic: str
    factual_hits: list[dict]
    theory_hits: list[dict]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/index")
def index_document(doc: dict) -> dict[str, str]:
    search_service.index(SearchDoc(id=doc["id"], text=doc["text"], metadata=doc.get("metadata", {})))
    return {"status": "indexed"}


@router.post("/search")
def semantic_search(req: SearchRequest) -> dict:
    hits = search_service.semantic(req.query)
    return {"results": [h.__dict__ for h in hits]}


@router.post("/analysis/budget-delta")
def budget(req: BudgetDiffRequest) -> dict:
    return budget_delta(req.old_rows, req.new_rows)


@router.post("/analysis/semantic-diff")
def sem_diff(req: SemanticDiffRequest) -> dict:
    changes = semantic_diff(req.old_sections, req.new_sections)
    return {"changes": [c.__dict__ for c in changes]}


@router.post("/briefs/organizer")
def organizer_brief(req: BriefRequest) -> dict:
    return generate_organizer_brief(req.topic, req.factual_hits, req.theory_hits)
