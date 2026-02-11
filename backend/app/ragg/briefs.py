from __future__ import annotations


def generate_organizer_brief(topic: str, factual_hits: list[dict], theory_hits: list[dict]) -> dict:
    return {
        "topic": topic,
        "label": "This is interpretive analysis grounded in sources.",
        "evidence": [
            {"text": h.get("text", ""), "citation": h.get("citation", {}), "source_type": "factual"}
            for h in factual_hits
        ],
        "interpretation": [
            {"text": h.get("text", ""), "citation": h.get("citation", {}), "source_type": "theory"}
            for h in theory_hits
        ],
        "action_options": [
            "Request testimony prep for next council session.",
            "Cross-check language with movement library precedent.",
        ],
    }
