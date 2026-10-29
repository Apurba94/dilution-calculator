"""Command-line interface for dilution-calculator."""
import argparse

from .core import (c1v1, fmt_mass, fmt_volume, mass_for_solution, molarity_from_mass, parse_quantity,
                   percent_solution, serial_dilution)

_C = {"molar": [("M", 1), ("mM", 1e-3), ("uM", 1e-6), ("nM", 1e-9), ("pM", 1e-12)],
      "massconc": [("mg/mL", 1), ("ug/mL", 1e-3), ("ng/mL", 1e-6)], "fold": [("X", 1)], "percent": [("%", 1)]}


def fmt_conc(v, kind):
    units = _C[kind]
    for u, f in units:
        if abs(v) >= f or u == units[-1][0]:
            return "%.4g %s" % (v / f, u)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dilution-calculator", description="Lab solution calculations.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dilute", help="C1V1 = C2V2 (leave one out)")
    for k in ("c1", "v1", "c2", "v2"):
        d.add_argument("--" + k)
    s = sub.add_parser("serial")
    s.add_argument("stock", help="e.g. '10 mM'")
    s.add_argument("fold", type=float)
    s.add_argument("steps", type=int)
    s.add_argument("final_volume", help="e.g. '1 mL'")
    m = sub.add_parser("mass", help="mass of solute for a molar solution")
    m.add_argument("molarity")
    m.add_argument("volume")
    m.add_argument("mw", type=float, help="g/mol")
    mo = sub.add_parser("molarity", help="molarity from mass, volume and MW")
    mo.add_argument("mass")
    mo.add_argument("volume")
    mo.add_argument("mw", type=float)
    p = sub.add_parser("percent", help="solute for a %% solution")
    p.add_argument("percent")
    p.add_argument("volume")
    p.add_argument("--vv", action="store_true", help="%% v/v instead of w/v")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "dilute":
            r = c1v1(args.c1, args.v1, args.c2, args.v2)
            given = args.c1 or args.c2
            kind = parse_quantity(given)[1] if given else "molar"
            print("Take %s of stock, add %s of diluent -> %s at %s" % (
                fmt_volume(r["v1"]), fmt_volume(r["diluent"]), fmt_volume(r["v2"]), fmt_conc(r["c2"], kind)))
            if r["solved"] in ("c1", "c2"):
                print("%s = %s" % (r["solved"], fmt_conc(r[r["solved"]], kind)))
        elif args.cmd == "serial":
            for row in serial_dilution(args.stock, args.fold, args.steps, args.final_volume):
                print("tube %2d: %-12s transfer %s + diluent %s" % (row["step"], fmt_conc(row["concentration"], row["kind"]),
                                                                  fmt_volume(row["transfer"]), fmt_volume(row["diluent"])))
        elif args.cmd == "mass":
            print("weigh %s" % fmt_mass(mass_for_solution(args.molarity, args.volume, args.mw)))
        elif args.cmd == "molarity":
            print(fmt_conc(molarity_from_mass(args.mass, args.volume, args.mw), "molar"))
        else:
            amount = percent_solution(args.percent, args.volume, "v/v" if args.vv else "w/v")
            print(("measure %s" % fmt_volume(amount)) if args.vv else ("weigh %s" % fmt_mass(amount)))
    except ValueError as exc:
        print("error: %s" % exc)
        return 1
    return 0
