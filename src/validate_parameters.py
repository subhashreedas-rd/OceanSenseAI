from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PARAMETER_PATH = (
    PROJECT_ROOT
    / "database"
    / "model_parameters"
    / "cai_2021_water_types.csv"
)

REQUIRED_COLUMNS = {
    "record_id",
    "source",
    "doi",
    "water_type",
    "wavelength_nm",
    "absorption_per_m",
    "scattering_per_m",
    "source_page",
    "source_role",
    "quality_flag",
    "permitted_use",
    "notes",
}


def load_parameter_records(
    path: Path = PARAMETER_PATH,
) -> list[dict[str, str]]:
    """Load and check the structure of a parameter table."""

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"No header was found in {path}.")

        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns: {missing}")

        records = list(reader)

    if not records:
        raise ValueError(f"No parameter records were found in {path}.")

    return records


def validate_numeric_values(record: dict[str, str]) -> tuple[float, float]:
    """Check that absorption and scattering values are physical."""

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

    return absorption, scattering


def classify_record(record: dict[str, str]) -> str:
    """Assign a data-use status from the provenance fields."""

    if (
        record["quality_flag"] == "internal_conflict"
        or record["permitted_use"] == "not_for_simulation"
    ):
        return "BLOCKED"

    if record["permitted_use"] != "simulation":
        return "REVIEW ONLY"

    return "APPROVED"


def main() -> None:
    records = load_parameter_records()

    status_counts = {
        "APPROVED": 0,
        "REVIEW ONLY": 0,
        "BLOCKED": 0,
    }

    for record in records:
        absorption, scattering = validate_numeric_values(record)
        attenuation = absorption + scattering
        status = classify_record(record)

        status_counts[status] += 1

        print(
            f"{record['record_id']} | "
            f"{record['water_type']} | "
            f"a = {absorption:.4f} m^-1 | "
            f"b = {scattering:.4f} m^-1 | "
            f"c = {attenuation:.4f} m^-1 | "
            f"{status}"
        )

    print("\nParameter-use summary")

    for status, count in status_counts.items():
        print(f"{status}: {count}")


if __name__ == "__main__":
    main()