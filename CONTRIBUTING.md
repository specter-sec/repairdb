# Contributing to RepairDB

Thanks for helping make repair learning clearer and safer. Keep pull requests small, explain what changed, and never imply that a sample record is an established defect without evidence scoped to the exact model and revision.

## Local validation

Install the test dependencies and validate the committed data as-is:

```bash
python -m pip install -e '.[test]'
PYTHONPATH=src python -m repairdb.validate
python -m pytest -q
python scripts/build_site.py
```

The ordinary contribution workflow is to edit the relevant `data/*.json` file directly, then validate and test it. Do **not** run the generator as a contribution prerequisite: `python scripts/generate_dataset.py` is an optional, destructive full reset that overwrites all seven data files from the generator templates. If you intentionally change those templates, test generated output in a temporary location with `python scripts/generate_dataset.py --output-dir /tmp/repairdb-generated` and review any proposed data changes explicitly before committing them.

If you add or change a field, update the JSON Schema, validator tests, and this template together. Keep each brand file under `data/` concise and valid JSON. CI validates the committed files and must not regenerate them before validation or deployment.

## Entry template

Use this shape and make every value specific enough to be useful while avoiding unsupported model claims:

```json
{
  "id": "brand-example-01",
  "brand": "Samsung",
  "model": "Galaxy A15",
  "title": "No charging — safe first checks",
  "symptom": "no charging",
  "likely_components": ["cable", "charging port", "battery"],
  "safe_diagnostic_steps": [
    "Inspect the disconnected cable and adapter for visible damage.",
    "Try a known-good, standards-compliant charger and observe the result."
  ],
  "tools": ["known-good charger", "bright flashlight"],
  "difficulty": "beginner",
  "estimated_cost_usd_parts_only": {"min": 0, "max": 45},
  "safety_notes": "Do not insert metal objects or charge a wet, swollen, or hot device.",
  "educational_example": true,
  "disclaimer": "Illustrative training example only; not a verified issue for this brand or model."
}
```

Use one of the schema's allowed symptoms: `no charging`, `no display`, `network issue`, `boot loop`, `no sound`, `overheating`, or `battery drain`. Difficulty is `beginner`, `intermediate`, or `advanced`. Cost fields are non-negative **sample USD parts-only ranges**, never labor-inclusive estimates, quotes, or guarantees. Real model names identify the illustrative device only; they do not imply that the symptom or possible components are known defects of that model.

## Content and safety standards

Start with reversible, non-invasive checks. Clearly mark uncertainty. Do not recommend battery puncture, bending, heating, improvised opening, board-level reflow, baseband or carrier-lock bypass, or unofficial firmware. Do not tell readers to wipe or unlock a device before discussing backup and data-loss risk. Escalate swelling, smoke, liquid exposure, severe heat, or damaged glass to qualified service. Read [`SAFETY.md`](SAFETY.md) for additional limits and emergency guidance.

If you make a verified model-specific claim in the future, include the exact model/variant and region, source URL and access date, what the source actually establishes, and any limits. Official safety documents are general safety guidance unless they explicitly document the claimed fault. Do not invent sources, quotations, or official verification.

## Pull requests and issues

Use the templates in `.github/`. A PR should state its evidence and scope, include validation output, and explain any safety impact. Please do not include personal information, IMEI/serial numbers, private repair records, or credentials in issue reports. Content concerns are welcome even when there is no proposed replacement text.
