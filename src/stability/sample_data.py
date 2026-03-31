"""Sample data generator — produces baseline and drifted CSV files.

The baseline has 25 rows with 5 diverse business columns.
The drifted load has 25 rows with 4 of 5 columns collapsed to a single value,
simulating a silent upstream failure where the pipeline looks healthy but
business signal has degraded.
"""

from __future__ import annotations

import csv
from pathlib import Path

MONITORED_COLUMNS = ["department", "region", "product_category", "status", "priority"]

# Diverse baseline values — 5 unique values per column
_DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "Operations"]
_REGIONS = ["West", "East", "Central", "South", "North"]
_CATEGORIES = ["Enterprise", "Mid-Market", "SMB", "Startup", "Government"]
_STATUSES = ["Active", "Pending", "Review", "Approved", "Closed"]
_PRIORITIES = ["Critical", "High", "Medium", "Low", "Deferred"]


def generate_baseline(n_rows: int = 25) -> list[dict]:
    """Generate a diverse baseline dataset."""
    rows: list[dict] = []
    for i in range(n_rows):
        rows.append({
            "record_id": f"REC-{1000 + i}",
            "department": _DEPARTMENTS[i % 5],
            "region": _REGIONS[i % 5],
            "product_category": _CATEGORIES[i % 5],
            "status": _STATUSES[i % 5],
            "priority": _PRIORITIES[i % 5],
            "amount": round(100.0 + i * 23.5, 2),
        })
    return rows


def generate_drifted(n_rows: int = 25) -> list[dict]:
    """Generate a drifted dataset — 4 of 5 monitored columns collapse.

    Only 'priority' retains its diversity. The other four columns default
    to a single value, simulating an upstream system failure where a source
    starts emitting constant values for most fields.
    """
    rows: list[dict] = []
    for i in range(n_rows):
        rows.append({
            "record_id": f"REC-{1000 + i}",
            "department": "Engineering",      # collapsed
            "region": "West",                 # collapsed
            "product_category": "Enterprise", # collapsed
            "status": "Active",               # collapsed
            "priority": _PRIORITIES[i % 5],   # still diverse
            "amount": round(100.0 + i * 23.5, 2),
        })
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_sample_data(output_dir: str | Path = "data/sample") -> None:
    """Write both sample datasets to CSV."""
    output_path = Path(output_dir)
    write_csv(generate_baseline(), output_path / "baseline.csv")
    write_csv(generate_drifted(), output_path / "drifted.csv")


if __name__ == "__main__":
    write_sample_data()
    print("Sample data written to data/sample/")
