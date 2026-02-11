from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClauseChange:
    clause_id: str
    change_type: str
    old_text: str
    new_text: str
    citation: dict


def semantic_diff(old_sections: dict[str, str], new_sections: dict[str, str]) -> list[ClauseChange]:
    changes: list[ClauseChange] = []
    old_by_text = {v: k for k, v in old_sections.items()}
    for new_id, new_text in new_sections.items():
        if new_id in old_sections:
            if old_sections[new_id] != new_text:
                changes.append(ClauseChange(new_id, "modified", old_sections[new_id], new_text, {"page": 1, "line_start": 1, "line_end": 8}))
        elif new_text in old_by_text:
            old_id = old_by_text[new_text]
            changes.append(ClauseChange(new_id, "moved", old_sections[old_id], new_text, {"page": 1, "line_start": 1, "line_end": 8}))
        else:
            changes.append(ClauseChange(new_id, "added", "", new_text, {"page": 1, "line_start": 1, "line_end": 8}))
    for old_id, old_text in old_sections.items():
        if old_id not in new_sections and old_text not in new_sections.values():
            changes.append(ClauseChange(old_id, "removed", old_text, "", {"page": 1, "line_start": 1, "line_end": 8}))
    return changes
