"""Validate RepairDB sample data using its published JSON Schema."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schema" / "repair-entry.schema.json"
DATA_DIR = ROOT / "data"
FILE_BRANDS = {
    "samsung": "Samsung",
    "xiaomi": "Xiaomi",
    "infinix": "Infinix",
    "tecno": "Tecno",
    "oppo": "Oppo",
    "vivo": "Vivo",
    "iphone": "iPhone",
}


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def validate_dataset(data_dir: Path = DATA_DIR, schema_path: Path = SCHEMA_PATH) -> list[str]:
    validator = Draft202012Validator(load_schema(schema_path))
    errors: list[str] = []
    data_files = sorted(data_dir.glob("*.json"))
    if not data_files:
        return [f"No JSON data files found in {data_dir}"]

    total_entries = 0
    seen_ids: dict[str, str] = {}
    for file_path in data_files:
        expected_brand = FILE_BRANDS.get(file_path.stem.lower())
        if expected_brand is None:
            errors.append(f"{file_path.name}: filename does not match a known brand data file")
        try:
            entries = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"{file_path.name}: {exc}")
            continue
        if not isinstance(entries, list):
            errors.append(f"{file_path.name}: expected a JSON array")
            continue
        total_entries += len(entries)
        for index, entry in enumerate(entries):
            prefix = f"{file_path.name}[{index}]"
            for error in validator.iter_errors(entry):
                location = ".".join(str(part) for part in error.absolute_path) or "entry"
                errors.append(f"{prefix}.{location}: {error.message}")

            if isinstance(entry, dict):
                brand = entry.get("brand")
                if expected_brand is not None and brand != expected_brand:
                    errors.append(f"{prefix}.brand: expected {expected_brand!r} to match filename, got {brand!r}")

                record_id = entry.get("id")
                if isinstance(record_id, str):
                    if record_id in seen_ids:
                        errors.append(
                            f"{prefix}.id: duplicate id {record_id!r}; first seen in {seen_ids[record_id]}"
                        )
                    else:
                        seen_ids[record_id] = prefix

                cost = entry.get("estimated_cost_usd_parts_only")
                if isinstance(cost, dict):
                    minimum = cost.get("min")
                    maximum = cost.get("max")
                    # JSON Schema reports malformed types. Compare only valid JSON
                    # numeric values so invalid lists/strings/null never crash validation.
                    is_number = lambda value: isinstance(value, (int, float)) and not isinstance(value, bool)
                    if is_number(minimum) and is_number(maximum) and minimum > maximum:
                        errors.append(f"{prefix}: cost min exceeds max")

    if total_entries == 0:
        errors.append(f"No dataset entries found in {data_dir}")
    return errors


def main() -> int:
    errors = validate_dataset()
    if errors:
        print("Dataset validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    total = sum(len(json.loads(path.read_text(encoding="utf-8"))) for path in DATA_DIR.glob("*.json"))
    print(f"Validated {total} entries against {SCHEMA_PATH.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
