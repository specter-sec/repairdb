from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from repairdb.validate import validate_dataset  # noqa: E402

BRANDS = {"Samsung", "Xiaomi", "Infinix", "Tecno", "Oppo", "Vivo", "iPhone"}
SYMPTOMS = {"no charging", "no display", "network issue", "boot loop", "no sound", "overheating", "battery drain"}


def load_records() -> list[dict]:
    return [entry for file in sorted((ROOT / "data").glob("*.json")) for entry in json.loads(file.read_text())]


def _write_dataset(directory: Path, records_by_file: dict[str, list[dict]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for filename, records in records_by_file.items():
        (directory / filename).write_text(json.dumps(records), encoding="utf-8")


def _record(brand: str, record_id: str) -> dict:
    source = json.loads((ROOT / "data" / f"{brand.lower()}.json").read_text(encoding="utf-8"))[0]
    result = copy.deepcopy(source)
    result["brand"] = brand
    result["id"] = record_id
    return result


def test_all_examples_validate_and_are_partitioned_by_brand() -> None:
    schema = json.loads((ROOT / "schema/repair-entry.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    records = load_records()
    assert len(records) == 42
    assert {record["brand"] for record in records} == BRANDS
    assert {record["symptom"] for record in records} == SYMPTOMS
    assert all(len([row for row in records if row["brand"] == brand]) == 6 for brand in BRANDS)
    assert len({record["id"] for record in records}) == len(records)
    assert all("series" not in record["model"].lower() and "family" not in record["model"].lower() for record in records)
    for record in records:
        validator.validate(record)
        assert record["educational_example"] is True
        assert "not a verified issue" in record["disclaimer"].lower()
        assert record["estimated_cost_usd_parts_only"]["min"] <= record["estimated_cost_usd_parts_only"]["max"]


def test_obvious_model_hardware_distinctions_are_only_generic_possibilities() -> None:
    records = load_records()
    samsung_oled_example = next(record for record in records if record["model"] == "Galaxy S24" and record["symptom"] == "no display")
    assert "backlight circuit" not in samsung_oled_example["likely_components"]
    assert "OLED display assembly" in samsung_oled_example["likely_components"]

    iphone_charging_examples = [record for record in records if record["brand"] == "iPhone" and record["symptom"] == "no charging"]
    port_components = {component for record in iphone_charging_examples for component in record["likely_components"]}
    assert "Lightning port or cable" in port_components
    assert "USB-C port or cable" in port_components
    assert all(record["educational_example"] is True for record in iphone_charging_examples)


def test_python_validator_cli() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "repairdb.validate"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validated 42 entries" in result.stdout


def test_generator_is_deterministic_without_overwriting_committed_data(tmp_path: Path) -> None:
    first_dir, second_dir = tmp_path / "first", tmp_path / "second"
    for directory in (first_dir, second_dir):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/generate_dataset.py"), "--output-dir", str(directory)],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    first = {path.name: path.read_bytes() for path in first_dir.glob("*.json")}
    second = {path.name: path.read_bytes() for path in second_dir.glob("*.json")}
    assert first == second
    assert sum(len(json.loads(path.read_text())) for path in first_dir.glob("*.json")) == 42


def test_malformed_cost_structures_are_reported_without_crashing(tmp_path: Path) -> None:
    malformed_values = [None, [], "not-a-cost-object", {"min": [], "max": 10}, {"min": "unknown", "max": 10}]
    for index, cost in enumerate(malformed_values):
        record = _record("Samsung", f"bad-cost-{index}")
        record["estimated_cost_usd_parts_only"] = cost
        directory = tmp_path / str(index)
        _write_dataset(directory, {"samsung.json": [record]})
        errors = validate_dataset(directory)
        assert errors
        assert any("estimated_cost_usd_parts_only" in error for error in errors)


def test_cost_minimum_greater_than_maximum_is_rejected(tmp_path: Path) -> None:
    record = _record("Samsung", "reversed-cost")
    record["estimated_cost_usd_parts_only"] = {"min": 12, "max": 4}
    _write_dataset(tmp_path, {"samsung.json": [record]})
    assert any("cost min exceeds max" in error for error in validate_dataset(tmp_path))


def test_duplicate_ids_across_brand_files_are_rejected(tmp_path: Path) -> None:
    _write_dataset(tmp_path, {
        "samsung.json": [_record("Samsung", "shared-id")],
        "xiaomi.json": [_record("Xiaomi", "shared-id")],
    })
    errors = validate_dataset(tmp_path)
    assert any("duplicate id 'shared-id'" in error for error in errors)


def test_brand_must_match_filename_and_unknown_files_are_rejected(tmp_path: Path) -> None:
    _write_dataset(tmp_path, {
        "samsung.json": [_record("Xiaomi", "wrong-brand")],
    })
    assert any("expected 'Samsung' to match filename" in error for error in validate_dataset(tmp_path))

    unknown_dir = tmp_path / "unknown"
    _write_dataset(unknown_dir, {"devices.json": [_record("Samsung", "unknown-file")]})
    assert any("filename does not match a known brand" in error for error in validate_dataset(unknown_dir))


def test_empty_dataset_is_rejected(tmp_path: Path) -> None:
    _write_dataset(tmp_path, {"samsung.json": []})
    assert any("No dataset entries found" in error for error in validate_dataset(tmp_path))


def test_no_dangerous_repair_instructions() -> None:
    text = " ".join(
        str(value).lower()
        for record in load_records()
        for key, value in record.items()
        if key in {"safety_notes", "safe_diagnostic_steps"}
    )
    assert "puncture" in text
    assert "do not puncture lithium cells" in text
    assert "do not puncture lithium cells, attempt board-level reflow, or bypass" in text
