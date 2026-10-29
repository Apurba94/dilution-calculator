"""Unit-aware solution chemistry calculations (concentration, volume, mass)."""
import re

CONC = {"M": 1.0, "mM": 1e-3, "uM": 1e-6, "µM": 1e-6, "nM": 1e-9, "pM": 1e-12,
        "g/L": None, "mg/mL": None, "ug/mL": None, "ng/mL": None, "mg/L": None, "x": None, "X": None, "%": None}
MASSCONC = {"g/L": 1.0, "mg/mL": 1.0, "ug/mL": 1e-3, "µg/mL": 1e-3, "ng/mL": 1e-6, "mg/L": 1e-3}
VOL = {"L": 1.0, "mL": 1e-3, "ml": 1e-3, "uL": 1e-6, "µL": 1e-6, "ul": 1e-6, "nL": 1e-9}
MASS = {"kg": 1e3, "g": 1.0, "mg": 1e-3, "ug": 1e-6, "µg": 1e-6, "ng": 1e-9}
_Q = re.compile(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(\S*)\s*$")


def parse_quantity(text):
    """'10 mM' -> (0.01, 'molar'); '250 uL' -> (0.00025, 'volume'); '5X' -> (5.0, 'fold'); '2%' -> (2.0, 'percent')."""
    m = _Q.match(str(text))
    if not m:
        raise ValueError("cannot parse %r" % text)
    v, u = float(m.group(1)), m.group(2)
    if u in ("M", "mM", "uM", "µM", "nM", "pM"):
        return v * CONC[u], "molar"
    if u in MASSCONC:
        return v * MASSCONC[u], "massconc"
    if u in VOL:
        return v * VOL[u], "volume"
    if u in MASS:
        return v * MASS[u], "mass"
    if u in ("x", "X"):
        return v, "fold"
    if u == "%":
        return v, "percent"
    raise ValueError("unknown unit %r in %r" % (u, text))


def fmt_volume(liters):
    for unit, f in (("L", 1.0), ("mL", 1e-3), ("uL", 1e-6), ("nL", 1e-9)):
        if abs(liters) >= f or unit == "nL":
            return "%.4g %s" % (liters / f, unit)


def fmt_mass(grams):
    for unit, f in (("kg", 1e3), ("g", 1.0), ("mg", 1e-3), ("ug", 1e-6), ("ng", 1e-9)):
        if abs(grams) >= f or unit == "ng":
            return "%.4g %s" % (grams / f, unit)


def c1v1(c1=None, v1=None, c2=None, v2=None):
    """Solve C1V1 = C2V2 for the missing argument (strings with units, e.g. '10 mM'). Returns dict."""
    vals = {"c1": c1, "v1": v1, "c2": c2, "v2": v2}
    missing = [k for k, v in vals.items() if v in (None, "")]
    if len(missing) != 1:
        raise ValueError("give exactly three of c1, v1, c2, v2")
    parsed = {k: parse_quantity(v) for k, v in vals.items() if v not in (None, "")}
    kinds = {k: p[1] for k, p in parsed.items()}
    ck = {kinds[k] for k in ("c1", "c2") if k in kinds}
    if len(ck) > 1:
        raise ValueError("c1 and c2 must use the same kind of unit (both molar, both mass/vol, both X or %)")
    if any(kinds[k] != "volume" for k in ("v1", "v2") if k in kinds):
        raise ValueError("v1 and v2 must be volumes")
    x = {k: p[0] for k, p in parsed.items()}
    m = missing[0]
    if m == "c1":
        x["c1"] = x["c2"] * x["v2"] / x["v1"]
    elif m == "v1":
        x["v1"] = x["c2"] * x["v2"] / x["c1"]
    elif m == "c2":
        x["c2"] = x["c1"] * x["v1"] / x["v2"]
    else:
        x["v2"] = x["c1"] * x["v1"] / x["c2"]
    if x["c2"] > x["c1"] + 1e-15:
        raise ValueError("final concentration cannot exceed the stock concentration")
    res = dict(x)
    res["solved"] = m
    res["diluent"] = x["v2"] - x["v1"]
    return res


def serial_dilution(stock, fold, steps, final_volume, transfer=None):
    """Serial dilution plan. Each tube ends with final_volume; transfer = final_volume / fold carried over.

    Returns list of dicts: step, concentration (stock units), transfer, diluent."""
    if fold <= 1:
        raise ValueError("fold must be > 1")
    c0, kind = parse_quantity(stock)
    vf, vk = parse_quantity(final_volume)
    if vk != "volume":
        raise ValueError("final_volume must be a volume")
    t = vf / fold if transfer is None else parse_quantity(transfer)[0]
    tube_volume = t * fold                  # volume made in each tube before transferring onward
    plan = []
    c = c0
    for i in range(1, steps + 1):
        c = c / fold
        plan.append({"step": i, "concentration": c, "kind": kind, "transfer": t, "diluent": tube_volume - t,
                     "remaining": tube_volume - (t if i < steps else 0)})
    return plan


def mass_for_solution(molarity, volume, mw):
    """Grams of solute for a solution: mass = M x V x MW."""
    c, k = parse_quantity(molarity)
    v, vk = parse_quantity(volume)
    if k != "molar" or vk != "volume":
        raise ValueError("need a molar concentration and a volume")
    return c * v * mw


def molarity_from_mass(mass, volume, mw):
    m, mk = parse_quantity(mass)
    v, vk = parse_quantity(volume)
    if mk != "mass" or vk != "volume":
        raise ValueError("need a mass and a volume")
    return m / mw / v


def percent_solution(percent, volume, kind="w/v"):
    """% w/v: grams per 100 mL. % v/v: mL per 100 mL. Returns grams or liters of solute."""
    v, vk = parse_quantity(volume)
    if vk != "volume":
        raise ValueError("need a volume")
    amount = float(str(percent).rstrip("%")) / 100 * v
    return amount * 1000 if kind == "w/v" else amount
