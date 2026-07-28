"""Validate the independent pure-water absorption benchmark dataset."""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT_DIR
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "sogandares_fry_1997.csv"
)

EXPECTED_ROW_COUNT = 31

EXPECTED_WAVELENGTHS = [
    float(wavelength)
    for wavelength in range(340, 641, 10)
]

EXPECTED_DOI = "10.1364/AO.36.008699"


def load_rows() -> list[dict[str, str]]:
    """Load the benchmark CSV file."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark dataset was not found: {DATA_PATH}"
        )

    with DATA_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Benchmark CSV does not contain a header"
            )

        return list(reader)


def validate_rows(
    rows: list[dict[str, str]],
) -> None:
    """Validate structure, metadata, values, and wavelength grid."""

    required_columns = {
        "dataset_id",
        "wavelength_nm",
        "property_symbol",
        "property_name",
        "value_per_m",
        "uncertainty_per_m",
        "error_percent",
        "optical_property_class",
        "medium",
        "temperature_C",
        "salinity_PSU",
        "measurement_method",
        "source_type",
        "uncertainty_reported",
        "study01_usable",
        "use_scope",
        "research_verdict",
        "citation",
        "doi",
        "source_url",
        "notes",
    }

    if not rows:
        raise ValueError(
            "Benchmark CSV contains no data rows"
        )

    missing_columns = required_columns - set(rows[0])

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"Benchmark CSV is missing columns: {missing}"
        )

    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_ROW_COUNT} rows, "
            f"found {len(rows)}"
        )

    expected_metadata = {
        "dataset_id": "OPD-001",
        "property_symbol": "a",
        "property_name": "absorption_coefficient",
        "optical_property_class": "inherent",
        "medium": "pure_water",
        "temperature_C": "25",
        "salinity_PSU": "0",
        "measurement_method": (
            "photothermal_deflection_spectroscopy"
        ),
        "source_type": "measured",
        "uncertainty_reported": "yes",
        "study01_usable": "yes",
        "use_scope": "absorption_only",
        "research_verdict": "Keep",
        "doi": EXPECTED_DOI,
    }

    wavelengths: list[float] = []

    for row_number, row in enumerate(
        rows,
        start=2,
    ):
        wavelength = float(row["wavelength_nm"])
        absorption = float(row["value_per_m"])
        uncertainty = float(row["uncertainty_per_m"])
        error_percent = float(row["error_percent"])
        temperature = float(row["temperature_C"])
        salinity = float(row["salinity_PSU"])

        numerical_values = {
            "wavelength_nm": wavelength,
            "value_per_m": absorption,
            "uncertainty_per_m": uncertainty,
            "error_percent": error_percent,
            "temperature_C": temperature,
            "salinity_PSU": salinity,
        }

        for column, value in numerical_values.items():
            if not math.isfinite(value):
                raise ValueError(
                    f"Row {row_number}: "
                    f"{column} must be finite"
                )

        if absorption <= 0.0:
            raise ValueError(
                f"Row {row_number}: "
                "absorption must be positive"
            )

        if uncertainty < 0.0:
            raise ValueError(
                f"Row {row_number}: "
                "uncertainty must be non-negative"
            )

        if error_percent < 0.0:
            raise ValueError(
                f"Row {row_number}: "
                "error percentage must be non-negative"
            )

        for column, expected_value in expected_metadata.items():
            actual_value = row[column].strip()

            if actual_value != expected_value:
                raise ValueError(
                    f"Row {row_number}: expected "
                    f"{column}={expected_value!r}, "
                    f"found {actual_value!r}"
                )

        wavelengths.append(wavelength)

    if wavelengths != EXPECTED_WAVELENGTHS:
        raise ValueError(
            "Benchmark wavelengths do not match the "
            "expected 340–640 nm grid at 10 nm intervals"
        )

    if len(set(wavelengths)) != len(wavelengths):
        raise ValueError(
            "Benchmark dataset contains duplicate wavelengths"
        )

    minimum_row = min(
        rows,
        key=lambda row: float(row["value_per_m"]),
    )

    minimum_wavelength = float(
        minimum_row["wavelength_nm"]
    )

    minimum_absorption = float(
        minimum_row["value_per_m"]
    )

    minimum_uncertainty = float(
        minimum_row["uncertainty_per_m"]
    )

    if minimum_wavelength != 420.0:
        raise ValueError(
            "Expected minimum absorption at 420 nm"
        )

    if not math.isclose(
        minimum_absorption,
        0.0062,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError(
            "Unexpected minimum absorption value"
        )

    if not math.isclose(
        minimum_uncertainty,
        0.0006,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError(
            "Unexpected uncertainty at the minimum"
        )


def main() -> None:
    """Run benchmark dataset validation."""

    rows = load_rows()
    validate_rows(rows)

    print(
        "Sogandares and Fry benchmark validation passed"
    )
    print(f"Rows: {len(rows)}")
    print("Wavelength range: 340–640 nm")
    print("Grid spacing: 10 nm")
    print(
        "Minimum absorption: "
        "0.0062 ± 0.0006 m^-1 at 420 nm"
    )
    print("Permitted use: absorption only")


if __name__ == "__main__":
    main()