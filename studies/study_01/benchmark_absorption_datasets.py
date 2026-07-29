"""Compare independent pure-water absorption datasets.

The analysis compares:

1. Mason, Cone, and Fry (2016), measured at 23 ± 0.5 °C.
2. Sogandares and Fry (1997), measured at 25 °C.

Only exact common wavelengths are compared. The original source datasets
are not interpolated or modified.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.pure_water_scattering import (  # noqa: E402
    molecular_scattering_coefficient,
)


MASON_PATH = (
    ROOT_DIR
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "mason_cone_fry_2016_pure_water_absorption.csv"
)

SOGANDARES_PATH = (
    ROOT_DIR
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "sogandares_fry_1997.csv"
)

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

OUTPUT_CSV_PATH = (
    RESULTS_DIR
    / "pure_water_absorption_dataset_benchmark.csv"
)

ABSORPTION_FIGURE_PATH = (
    FIGURES_DIR
    / "pure_water_absorption_dataset_benchmark.png"
)

ATTENUATION_FIGURE_PATH = (
    FIGURES_DIR
    / "pure_water_attenuation_dataset_sensitivity.png"
)

MINIMUM_WAVELENGTH_NM = 350.0
MAXIMUM_WAVELENGTH_NM = 550.0
WAVELENGTH_INTERVAL_NM = 10.0

MASON_TEMPERATURE_C = 23.0
SOGANDARES_TEMPERATURE_C = 25.0

DEPOLARISATION_RATIO = 0.039


def load_mason_data() -> dict[float, dict[str, float]]:
    """Load Mason et al. values at exact 10 nm wavelengths."""

    required_columns = {
        "wavelength_nm",
        "absorption_per_m",
        "uncertainty_per_m",
    }

    with MASON_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Mason dataset does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))

            raise ValueError(
                f"Mason dataset is missing columns: {missing}"
            )

        data: dict[float, dict[str, float]] = {}

        for row_number, row in enumerate(reader, start=2):
            wavelength = float(row["wavelength_nm"])
            absorption = float(row["absorption_per_m"])
            uncertainty = float(row["uncertainty_per_m"])

            if not (
                MINIMUM_WAVELENGTH_NM
                <= wavelength
                <= MAXIMUM_WAVELENGTH_NM
            ):
                continue

            wavelength_remainder = math.fmod(
                wavelength,
                WAVELENGTH_INTERVAL_NM,
            )

            if not math.isclose(
                wavelength_remainder,
                0.0,
                rel_tol=0.0,
                abs_tol=1.0e-9,
            ):
                continue

            if wavelength in data:
                raise ValueError(
                    "Duplicate Mason wavelength found: "
                    f"{wavelength:.0f} nm"
                )

            if absorption <= 0.0:
                raise ValueError(
                    f"Mason row {row_number}: "
                    "absorption must be positive"
                )

            if uncertainty < 0.0:
                raise ValueError(
                    f"Mason row {row_number}: "
                    "uncertainty must be non-negative"
                )

            data[wavelength] = {
                "absorption_per_m": absorption,
                "uncertainty_per_m": uncertainty,
            }

    return data


def load_sogandares_data() -> dict[float, dict[str, float]]:
    """Load Sogandares and Fry values over the common range."""

    required_columns = {
        "wavelength_nm",
        "value_per_m",
        "uncertainty_per_m",
    }

    with SOGANDARES_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Sogandares dataset does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))

            raise ValueError(
                "Sogandares dataset is missing columns: "
                f"{missing}"
            )

        data: dict[float, dict[str, float]] = {}

        for row_number, row in enumerate(reader, start=2):
            wavelength = float(row["wavelength_nm"])
            absorption = float(row["value_per_m"])
            uncertainty = float(row["uncertainty_per_m"])

            if not (
                MINIMUM_WAVELENGTH_NM
                <= wavelength
                <= MAXIMUM_WAVELENGTH_NM
            ):
                continue

            if wavelength in data:
                raise ValueError(
                    "Duplicate Sogandares wavelength found: "
                    f"{wavelength:.0f} nm"
                )

            if absorption <= 0.0:
                raise ValueError(
                    f"Sogandares row {row_number}: "
                    "absorption must be positive"
                )

            if uncertainty < 0.0:
                raise ValueError(
                    f"Sogandares row {row_number}: "
                    "uncertainty must be non-negative"
                )

            data[wavelength] = {
                "absorption_per_m": absorption,
                "uncertainty_per_m": uncertainty,
            }

    return data


def expected_common_wavelengths() -> list[float]:
    """Return the expected 350–550 nm grid."""

    return [
        float(wavelength)
        for wavelength in range(350, 551, 10)
    ]


def build_comparison_rows() -> list[dict[str, float]]:
    """Combine both datasets at exact common wavelengths."""

    mason_data = load_mason_data()
    sogandares_data = load_sogandares_data()

    wavelengths = expected_common_wavelengths()

    if sorted(mason_data) != wavelengths:
        raise ValueError(
            "Mason data do not match the expected "
            "350–550 nm grid at 10 nm intervals"
        )

    if sorted(sogandares_data) != wavelengths:
        raise ValueError(
            "Sogandares data do not match the expected "
            "350–550 nm grid at 10 nm intervals"
        )

    rows: list[dict[str, float]] = []

    for wavelength in wavelengths:
        mason_absorption = mason_data[
            wavelength
        ]["absorption_per_m"]

        mason_uncertainty = mason_data[
            wavelength
        ]["uncertainty_per_m"]

        sogandares_absorption = sogandares_data[
            wavelength
        ]["absorption_per_m"]

        sogandares_uncertainty = sogandares_data[
            wavelength
        ]["uncertainty_per_m"]

        difference = (
            sogandares_absorption
            - mason_absorption
        )

        relative_difference = (
            difference / mason_absorption
        )

        absolute_relative_difference = abs(
            relative_difference
        )

        combined_uncertainty = math.sqrt(
            mason_uncertainty**2
            + sogandares_uncertainty**2
        )

        if combined_uncertainty > 0.0:
            normalised_difference = (
                difference / combined_uncertainty
            )
        else:
            normalised_difference = math.nan

        mason_scattering = (
            molecular_scattering_coefficient(
                wavelength_nm=wavelength,
                temperature_c=MASON_TEMPERATURE_C,
                delta=DEPOLARISATION_RATIO,
            )
        )

        sogandares_scattering = (
            molecular_scattering_coefficient(
                wavelength_nm=wavelength,
                temperature_c=SOGANDARES_TEMPERATURE_C,
                delta=DEPOLARISATION_RATIO,
            )
        )

        mason_attenuation = (
            mason_absorption
            + mason_scattering
        )

        sogandares_attenuation = (
            sogandares_absorption
            + sogandares_scattering
        )

        rows.append(
            {
                "wavelength_nm": wavelength,
                "mason_absorption_per_m": (
                    mason_absorption
                ),
                "mason_uncertainty_per_m": (
                    mason_uncertainty
                ),
                "sogandares_absorption_per_m": (
                    sogandares_absorption
                ),
                "sogandares_uncertainty_per_m": (
                    sogandares_uncertainty
                ),
                "sogandares_minus_mason_per_m": (
                    difference
                ),
                "relative_difference_vs_mason": (
                    relative_difference
                ),
                "absolute_relative_difference": (
                    absolute_relative_difference
                ),
                "combined_absorption_uncertainty_per_m": (
                    combined_uncertainty
                ),
                "normalised_absorption_difference": (
                    normalised_difference
                ),
                "mason_scattering_per_m": (
                    mason_scattering
                ),
                "sogandares_scattering_per_m": (
                    sogandares_scattering
                ),
                "mason_total_attenuation_per_m": (
                    mason_attenuation
                ),
                "sogandares_total_attenuation_per_m": (
                    sogandares_attenuation
                ),
            }
        )

    return rows


def write_results(
    rows: list[dict[str, float]],
) -> None:
    """Write the comparison results to CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "wavelength_nm",
        "mason_absorption_per_m",
        "mason_uncertainty_per_m",
        "sogandares_absorption_per_m",
        "sogandares_uncertainty_per_m",
        "sogandares_minus_mason_per_m",
        "relative_difference_vs_mason",
        "absolute_relative_difference",
        "combined_absorption_uncertainty_per_m",
        "normalised_absorption_difference",
        "mason_scattering_per_m",
        "sogandares_scattering_per_m",
        "mason_total_attenuation_per_m",
        "sogandares_total_attenuation_per_m",
    ]

    with OUTPUT_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            formatted_row = {
                "wavelength_nm": (
                    f"{row['wavelength_nm']:.1f}"
                ),
            }

            for fieldname in fieldnames[1:]:
                formatted_row[fieldname] = (
                    f"{row[fieldname]:.12e}"
                )

            writer.writerow(formatted_row)


def create_absorption_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot both source-reported absorption spectra."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    mason_absorption = [
        row["mason_absorption_per_m"]
        for row in rows
    ]

    mason_uncertainty = [
        row["mason_uncertainty_per_m"]
        for row in rows
    ]

    sogandares_absorption = [
        row["sogandares_absorption_per_m"]
        for row in rows
    ]

    sogandares_uncertainty = [
        row["sogandares_uncertainty_per_m"]
        for row in rows
    ]

    figure, axis = plt.subplots(
        figsize=(9.0, 6.0)
    )

    axis.errorbar(
        wavelengths,
        mason_absorption,
        yerr=mason_uncertainty,
        marker="o",
        markersize=4,
        capsize=2,
        label="Mason et al. (2016), 23 °C",
    )

    axis.errorbar(
        wavelengths,
        sogandares_absorption,
        yerr=sogandares_uncertainty,
        marker="s",
        markersize=4,
        capsize=2,
        label="Sogandares and Fry (1997), 25 °C",
    )

    axis.set_yscale("log")

    axis.set_xlabel("Wavelength (nm)")

    axis.set_ylabel(
        "Pure-water absorption coefficient "
        "(m$^{-1}$)"
    )

    axis.set_title(
        "Independent pure-water absorption datasets"
    )

    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        ABSORPTION_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_attenuation_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot total attenuation derived from each absorption source."""

    wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    mason_attenuation = [
        row["mason_total_attenuation_per_m"]
        for row in rows
    ]

    sogandares_attenuation = [
        row["sogandares_total_attenuation_per_m"]
        for row in rows
    ]

    figure, axis = plt.subplots(
        figsize=(9.0, 6.0)
    )

    axis.plot(
        wavelengths,
        mason_attenuation,
        marker="o",
        markersize=4,
        label=(
            "Mason absorption + scattering "
            "at 23 °C"
        ),
    )

    axis.plot(
        wavelengths,
        sogandares_attenuation,
        marker="s",
        markersize=4,
        label=(
            "Sogandares absorption + scattering "
            "at 25 °C"
        ),
    )

    axis.set_xlabel("Wavelength (nm)")

    axis.set_ylabel(
        "Calculated beam attenuation coefficient "
        "(m$^{-1}$)"
    )

    axis.set_title(
        "Sensitivity of total attenuation "
        "to absorption dataset"
    )

    axis.grid(alpha=0.3)

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        ATTENUATION_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def find_minimum(
    rows: list[dict[str, float]],
    fieldname: str,
) -> dict[str, float]:
    """Return the row containing the minimum value."""

    return min(
        rows,
        key=lambda row: row[fieldname],
    )


def calculate_median(
    values: list[float],
) -> float:
    """Calculate the median without external dependencies."""

    sorted_values = sorted(values)
    count = len(sorted_values)
    midpoint = count // 2

    if count % 2 == 1:
        return sorted_values[midpoint]

    return (
        sorted_values[midpoint - 1]
        + sorted_values[midpoint]
    ) / 2.0


def print_summary(
    rows: list[dict[str, float]],
) -> None:
    """Print the main comparison results."""

    mason_absorption_minimum = find_minimum(
        rows,
        "mason_absorption_per_m",
    )

    sogandares_absorption_minimum = find_minimum(
        rows,
        "sogandares_absorption_per_m",
    )

    mason_attenuation_minimum = find_minimum(
        rows,
        "mason_total_attenuation_per_m",
    )

    sogandares_attenuation_minimum = find_minimum(
        rows,
        "sogandares_total_attenuation_per_m",
    )

    absolute_relative_differences = [
        row["absolute_relative_difference"]
        for row in rows
    ]

    mean_absolute_relative_difference = (
        sum(absolute_relative_differences)
        / len(absolute_relative_differences)
    )

    median_absolute_relative_difference = (
        calculate_median(
            absolute_relative_differences
        )
    )

    within_two_combined_uncertainties = sum(
        1
        for row in rows
        if abs(
            row["normalised_absorption_difference"]
        )
        <= 2.0
    )

    print()
    print("Pure-water absorption dataset benchmark")
    print("---------------------------------------")
    print(f"Common wavelengths: {len(rows)}")
    print("Comparison range: 350–550 nm")
    print("Grid spacing: 10 nm")
    print("Interpolation: none")

    print()
    print("Absorption minima on the common grid")

    print(
        "Mason et al. (2016): "
        f"{mason_absorption_minimum['wavelength_nm']:.0f} nm, "
        f"{mason_absorption_minimum['mason_absorption_per_m']:.6f} "
        "m^-1"
    )

    print(
        "Sogandares and Fry (1997): "
        f"{sogandares_absorption_minimum['wavelength_nm']:.0f} nm, "
        f"{sogandares_absorption_minimum['sogandares_absorption_per_m']:.6f} "
        "m^-1"
    )

    print()
    print("Calculated total-attenuation minima")

    print(
        "Using Mason absorption at 23 °C: "
        f"{mason_attenuation_minimum['wavelength_nm']:.0f} nm, "
        f"{mason_attenuation_minimum['mason_total_attenuation_per_m']:.6f} "
        "m^-1"
    )

    print(
        "Using Sogandares absorption at 25 °C: "
        f"{sogandares_attenuation_minimum['wavelength_nm']:.0f} nm, "
        f"{sogandares_attenuation_minimum['sogandares_total_attenuation_per_m']:.6f} "
        "m^-1"
    )

    print()
    print(
        "Mean absolute relative absorption difference: "
        f"{mean_absolute_relative_difference * 100.0:.2f} %"
    )

    print(
        "Median absolute relative absorption difference: "
        f"{median_absolute_relative_difference * 100.0:.2f} %"
    )

    print(
        "Wavelengths within two combined source uncertainties: "
        f"{within_two_combined_uncertainties}/{len(rows)}"
    )

    print()
    print(
        "Important: the datasets were measured at different "
        "temperatures and using different experimental methods. "
        "No temperature correction has been applied."
    )

    print()
    print(f"Saved results: {OUTPUT_CSV_PATH}")
    print(
        f"Saved absorption figure: "
        f"{ABSORPTION_FIGURE_PATH}"
    )
    print(
        f"Saved attenuation figure: "
        f"{ATTENUATION_FIGURE_PATH}"
    )


def main() -> None:
    """Run the full-spectrum absorption benchmark."""

    rows = build_comparison_rows()

    write_results(rows)
    create_absorption_figure(rows)
    create_attenuation_figure(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()