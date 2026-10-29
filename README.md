# dilution-calculator

**The bench calculator you always need: C1V1 = C2V2 with units, serial dilution plans,
mass for a molar solution, molarity from mass, and percent solutions.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Dilution arithmetic is simple, but unit conversions (mM to uM, mL to uL) under time pressure are
a classic source of 1000-fold errors. A unit-aware calculator that prints the pipetting instruction
directly ("take 10 uL of stock, add 990 uL of diluent") removes the mental arithmetic, and its tests
document the calculations.

## Features

- `dilute`: solve C1V1 = C2V2 for any one unknown, with molar (M ... pM), mass/volume (mg/mL, ug/mL, ng/mL),
  fold (10X) or percent concentrations and L/mL/uL/nL volumes; refuses impossible "dilutions"
- `serial`: n-step serial dilution with fold, final volume per tube, transfer and diluent volumes
- `mass`: grams to weigh for M x V x MW; `molarity`: concentration from a weighed mass
- `percent`: % w/v (grams per 100 mL) and % v/v
- Human-friendly output units

## Usage

```bash
pip install .
dilution-calculator dilute --c1 "10 mM" --c2 "100 uM" --v2 "1 mL"
dilution-calculator serial "1 mg/mL" 2 8 "200 uL"
dilution-calculator mass "150 mM" "500 mL" 58.44
dilution-calculator percent 1% "100 mL"
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
