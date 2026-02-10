import sys
import unittest
from pathlib import Path

# Import the demo Terrain directly from product/src
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "product" / "src"))

import tax_calculator  # noqa: E402


class TestTaxCalculator(unittest.TestCase):
    def test_normalize_country_strips_and_upcases(self) -> None:
        self.assertEqual(tax_calculator.normalize_country(" us "), "US")

    def test_calculate_tax_uses_rate(self) -> None:
        self.assertAlmostEqual(tax_calculator.calculate_tax(100.0, "US", 0.1), 10.0)


if __name__ == "__main__":
    unittest.main()
