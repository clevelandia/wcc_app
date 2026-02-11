from __future__ import annotations


def budget_delta(old_rows: list[dict], new_rows: list[dict], key: str = "account") -> dict:
    old_map = {row[key]: row for row in old_rows}
    new_map = {row[key]: row for row in new_rows}
    changes = []
    for acct, new_row in new_map.items():
        old_row = old_map.get(acct, {})
        before = float(old_row.get("amount", 0))
        after = float(new_row.get("amount", 0))
        if before != after:
            changes.append({"account": acct, "before": before, "after": after, "delta": after - before, "provenance": new_row.get("provenance", {})})
    return {"changes": changes}
