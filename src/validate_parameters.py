from __future__ import annotations

import csv
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PARAMETER_TABLES = [
    PROJECT_ROOT
    / "database"
    / "model_parameters"
    / "cai_2021_water_types.csv",
    PROJECT_ROOT
    / "database"
    / "model_parameters"
    / "wang_2021_water_types.csv",
]

REQUIRED_COLUMNS = {
    "record_id",
    "source",
    "doi",
    "water_type",
    "absorption_per_m",
    "scattering_per_m",
    "quality_flag",
    "permitted_use",
}


def load_parameter_records(path: Path) -> list[dict[str, str]]:
    """Load a parameter table and check its required columns."""

    if not path.exists():
        raise FileNotFoundError(f"Parameter table not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"No header was found in {path}.")

        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"{path.name} is missing required columns: {missing}"
            )

        records = list(reader)

    if not records:
        raise ValueError(f"No parameter records were found in {path}.")

    return records


def validate_numeric_values(
    record: dict[str, str],
) -> tuple[float, float, float]:
    """Check optical coefficients and calculate attenuation."""

    absorption = float(record["absorption_per_m"])
    scattering = float(record["scattering_per_m"])

    if absorption < 0:
        raise ValueError(
            f"{record['record_id']}: absorption cannot be negative."
        )

    if scattering < 0:
        raise ValueError(
            f"{record['record_id']}: scattering cannot be negative."
        )

    attenuation = absorption + scattering

    return absorption, scattering, attenuation


def validate_reported_attenuation(
    record: dict[str, str],
    calculated_attenuation: float,
) -> str:
    """Compare reported attenuation with absorption plus scattering."""

    reported_value = record.get("reported_attenuation_per_m", "").strip()

    if not reported_value:
        return "not reported"

    reported_attenuation = float(reported_value)

    if not math.isclose(
        calculated_attenuation,
        reported_attenuation,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            f"{record['record_id']}: reported attenuation "
            f"{reported_attenuation:.4f} m^-1 does not equal "
            f"a + b = {calculated_attenuation:.4f} m^-1."
        )

    return f"{reported_attenuation:.4f} m^-1, consistent"


def classify_record(record: dict[str, str]) -> str:
    """Assign a use status from provenance information."""

    if (
        record["quality_flag"] == "internal_conflict"
        or record["permitted_use"] == "not_for_simulation"
    ):
        return "BLOCKED"

    if record["permitted_use"] != "simulation":
        return "REVIEW ONLY"

    return "APPROVED"


def validate_table(path: Path) -> None:
    """Validate one parameter table and print its status."""

    records = load_parameter_records(path)

    status_counts = {
        "APPROVED": 0,
        "REVIEW ONLY": 0,
        "BLOCKED": 0,
    }

    print(f"\nTable: {path.name}")

    for record in records:
        absorption, scattering, attenuation = validate_numeric_values(record)

        reported_status = validate_reported_attenuation(
            record=record,
            calculated_attenuation=attenuation,
        )

        use_status = classify_record(record)
        status_counts[use_status] += 1

        print(
            f"{record['record_id']} | "
            f"{record['water_type']} | "
            f"a = {absorption:.4f} m^-1 | "
            f"b = {scattering:.4f} m^-1 | "
            f"c = {attenuation:.4f} m^-1 | "
            f"reported c: {reported_status} | "
            f"{use_status}"
        )

    print("Status summary")

    for status, count in status_counts.items():
        print(f"{status}: {count}")


def main() -> None:
    for table_path in PARAMETER_TABLES:
        validate_table(table_path)


if __name__ == "__main__":
    main()