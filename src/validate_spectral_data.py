from __future__ import annotations

import csv
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "mason_cone_fry_2016_pure_water_absorption.csv"
)

EXPECTED_COLUMNS = {
    "record_id",
    "source",
    "doi",
    "wavelength_nm",
    "absorption_per_m",
    "uncertainty_per_m",
    "temperature_C",
    "medium",
    "measurement_method",
    "source_table",
    "source_role",
    "quality_flag",
    "permitted_use",
    "notes",
}

EXPECTED_DOI = "10.1364/AO.55.007163"
EXPECTED_SOURCE = "Mason_Cone_Fry_2016"


def load_records(path: Path) -> list[dict[str, str]]:
    """Load the spectral absorption dataset."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("The dataset does not contain a header.")

        missing_columns = EXPECTED_COLUMNS.difference(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns: {missing}")

        records = list(reader)

    if not records:
        raise ValueError("The dataset contains no records.")

    return records


def expected_wavelengths() -> list[int]:
    """Return the wavelength grid reported in Table 2."""

    ultraviolet_grid = list(range(250, 301, 10))
    fine_grid = list(range(302, 551, 2))

    return ultraviolet_grid + fine_grid


def validate_metadata(record: dict[str, str]) -> None:
    """Check source and permitted-use metadata."""

    record_id = record["record_id"]

    if record["source"] != EXPECTED_SOURCE:
        raise ValueError(f"{record_id}: unexpected source.")

    if record["doi"] != EXPECTED_DOI:
        raise ValueError(f"{record_id}: unexpected DOI.")

    if record["medium"] != "pure_water":
        raise ValueError(f"{record_id}: medium must be pure_water.")

    if record["source_table"] != "Table_2":
        raise ValueError(f"{record_id}: source table must be Table_2.")

    if record["source_role"] != "primary_experimental_dataset":
        raise ValueError(f"{record_id}: unexpected source role.")

    if record["quality_flag"] != "source_reported":
        raise ValueError(f"{record_id}: unexpected quality flag.")

    if record["permitted_use"] != "absorption_only":
        raise ValueError(
            f"{record_id}: dataset must remain absorption-only."
        )


def validate_dataset(records: list[dict[str, str]]) -> None:
    """Validate structure, values, provenance, and wavelength coverage."""

    if len(records) != 131:
        raise ValueError(
            f"Expected 131 records, but found {len(records)}."
        )

    record_ids: list[str] = []
    wavelengths: list[int] = []
    absorption_values: list[float] = []

    for record in records:
        validate_metadata(record)

        record_id = record["record_id"]
        wavelength = int(record["wavelength_nm"])
        absorption = float(record["absorption_per_m"])
        uncertainty = float(record["uncertainty_per_m"])

        if absorption <= 0:
            raise ValueError(
                f"{record_id}: absorption must be greater than zero."
            )

        if uncertainty < 0:
            raise ValueError(
                f"{record_id}: uncertainty cannot be negative."
            )

        record_ids.append(record_id)
        wavelengths.append(wavelength)
        absorption_values.append(absorption)

    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Duplicate record IDs were found.")

    if len(wavelengths) != len(set(wavelengths)):
        raise ValueError("Duplicate wavelengths were found.")

    if wavelengths != sorted(wavelengths):
        raise ValueError("Wavelengths are not strictly increasing.")

    expected = expected_wavelengths()

    if wavelengths != expected:
        raise ValueError(
            "The wavelength grid does not match the source table."
        )

    minimum_index = absorption_values.index(min(absorption_values))
    minimum_wavelength = wavelengths[minimum_index]
    minimum_absorption = absorption_values[minimum_index]

    if minimum_wavelength != 344:
        raise ValueError(
            f"Expected minimum at 344 nm, found {minimum_wavelength} nm."
        )

    if not math.isclose(
        minimum_absorption,
        0.000810,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError(
            "Minimum absorption does not match the rounded Table 2 value."
        )

    print("Spectral dataset validation")
    print(f"Source: {EXPECTED_SOURCE}")
    print(f"DOI: {EXPECTED_DOI}")
    print(f"Rows: {len(records)}")
    print(f"Range: {wavelengths[0]}-{wavelengths[-1]} nm")
    print("Grid: 10 nm from 250-300 nm; 2 nm from 302-550 nm")
    print(
        f"Minimum: {minimum_wavelength} nm, "
        f"{minimum_absorption:.6f} m^-1"
    )
    print("Permitted use: absorption-only analysis")
    print("Validation status: PASSED")


def main() -> None:
    records = load_records(DATA_PATH)
    validate_dataset(records)


if __name__ == "__main__":
    main()