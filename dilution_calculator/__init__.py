"""Everyday lab calculations: C1V1 = C2V2, serial dilutions, molarity and mass."""
from .core import parse_quantity, c1v1, serial_dilution, mass_for_solution, molarity_from_mass, percent_solution

__version__ = "0.1.0"
__all__ = ["parse_quantity", "c1v1", "serial_dilution", "mass_for_solution", "molarity_from_mass", "percent_solution"]
