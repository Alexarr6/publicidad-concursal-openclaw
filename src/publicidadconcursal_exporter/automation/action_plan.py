from __future__ import annotations

from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parent / "plans"


def load_plan(plan_name: str) -> str:
    """Load a browser action plan file from automation/plans."""

    plan_path = PLAN_DIR / f"{plan_name}.md"
    if not plan_path.exists():
        raise FileNotFoundError(f"Action plan not found: {plan_path}")
    return plan_path.read_text(encoding="utf-8").strip()
