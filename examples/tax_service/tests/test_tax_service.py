# Demo test anchor for Chapter 6 slicing.
#
# This file is used as an anchor node in slice packets; it is not part of the repo's default test suite.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tax_service import calculate_income_tax  # noqa: E402


def test_calculate_income_tax_high_earner_scenario() -> None:
    income = 150000
    expected_tax = 30000  # 50k*0.1 + 50k*0.2 + 50k*0.3
    actual_tax = calculate_income_tax(income)
    assert abs(actual_tax - expected_tax) < 1e-6
