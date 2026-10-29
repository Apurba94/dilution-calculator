import io
import unittest
from contextlib import redirect_stdout

from dilution_calculator.cli import main
from dilution_calculator.core import (c1v1, mass_for_solution, molarity_from_mass, parse_quantity, percent_solution,
                                      serial_dilution)


class ParseTests(unittest.TestCase):
    def test_units(self):
        self.assertEqual(parse_quantity("10 mM"), (0.01, "molar"))
        self.assertAlmostEqual(parse_quantity("250uL")[0], 2.5e-4)
        self.assertEqual(parse_quantity("5X"), (5.0, "fold"))
        with self.assertRaises(ValueError):
            parse_quantity("3 furlongs")


class DilutionTests(unittest.TestCase):
    def test_solve_v1(self):
        r = c1v1(c1="10 mM", c2="100 uM", v2="1 mL")
        self.assertAlmostEqual(r["v1"], 1e-5)        # 10 uL
        self.assertAlmostEqual(r["diluent"], 9.9e-4)

    def test_solve_other_unknowns(self):
        self.assertAlmostEqual(c1v1(c1="10X", v1="5 mL", v2="50 mL")["c2"], 1.0)
        self.assertAlmostEqual(c1v1(v1="2 uL", c2="1 ug/mL", v2="200 uL")["c1"], 0.1)   # 100 ug/mL in g/L units

    def test_errors(self):
        with self.assertRaises(ValueError):
            c1v1(c1="1 mM", c2="10 mM", v2="1 mL")           # cannot concentrate by diluting
        with self.assertRaises(ValueError):
            c1v1(c1="1 mM", c2="1 mg/mL", v2="1 mL")         # mixed kinds
        with self.assertRaises(ValueError):
            c1v1(c1="1 mM", v2="1 mL")

    def test_serial(self):
        plan = serial_dilution("1 mM", 10, 3, "1 mL")
        self.assertEqual([round(p["concentration"] * 1e6, 6) for p in plan], [100.0, 10.0, 1.0])   # uM
        self.assertAlmostEqual(plan[0]["transfer"], 1e-4)
        self.assertAlmostEqual(plan[0]["diluent"], 9e-4)
        with self.assertRaises(ValueError):
            serial_dilution("1 mM", 1, 3, "1 mL")

    def test_mass_molarity_percent(self):
        self.assertAlmostEqual(mass_for_solution("150 mM", "500 mL", 58.44), 4.383)       # NaCl
        self.assertAlmostEqual(molarity_from_mass("4.383 g", "500 mL", 58.44), 0.15)
        self.assertAlmostEqual(percent_solution("1%", "100 mL"), 1.0)                     # 1 g agarose
        self.assertAlmostEqual(percent_solution("70%", "100 mL", "v/v"), 0.07)            # 70 mL ethanol

    def test_cli(self):
        with redirect_stdout(io.StringIO()) as buf:
            main(["dilute", "--c1", "10 mM", "--c2", "100 uM", "--v2", "1 mL"])
            main(["mass", "150 mM", "500 mL", "58.44"])
            main(["serial", "1 mM", "10", "2", "1 mL"])
        out = buf.getvalue()
        self.assertIn("Take 10 uL of stock, add 990 uL of diluent -> 1 mL at 100 uM", out)
        self.assertIn("weigh 4.383 g", out)
        self.assertIn("tube  2: 10 uM", out)


if __name__ == "__main__":
    unittest.main()
