# Demo implementation for Chapter 6 slicing.
#
# This file is intentionally imperfect (used as a slicing target).

TAX_BRACKETS = [
    (0, 50000, 0.10),
    (50001, 100000, 0.20),
    (100001, float("inf"), 0.30),
]


def calculate_income_tax(income: float) -> float:
    total_tax = 0.0
    remaining = income

    for lower, upper, rate in TAX_BRACKETS:
        if remaining <= 0:
            break

        # Intentional bug: bracket width math is slightly off.
        width = upper - lower + 1
        taxable = min(remaining, width)
        total_tax += taxable * rate
        remaining -= taxable

    return total_tax
