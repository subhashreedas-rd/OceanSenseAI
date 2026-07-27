"""Combine pure-water absorption and molecular scattering spectra."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.pure_water_scattering import (  # noqa: E402
    molecular_scattering_coefficient,
)


ABSORPTION_DATA_PATH = (
    ROOT_DIR
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "mason_cone_fry_2016_pure_water_absorption.csv"
)

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

OUTPUT_CSV_PATH = (
    RESULTS_DIR / "pure_water_total_attenuation_spectrum.csv"
)

OUTPUT_FIGURE_PATH = (
    FIGURES_DIR
    / "pure_water_absorption_scattering_attenuation.png"
)

TEMPERATURE_C = 23.0
DEPOLARIZATION_RATIO = 0.039

MIN_WAVELENGTH_NM = 350
MAX_WAVELENGTH_NM = 550
WAVELENGTH_STEP_NM = 2


def load_absorption_data() -> list[dict[str, float]]:
    """Load and validate the overlapping absorption measurements."""

    required_columns = {
        "wavelength_nm",
        "absorption_per_m",
        "uncertainty_per_m",
        "temperature_C",
        "permitted_use",
    }

    with ABSORPTION_DATA_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Absorption CSV does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Absorption CSV is missing columns: {missing}"
            )

        rows: list[dict[str, float]] = []

        for source_row in reader:
            wavelength_nm = float(source_row["wavelength_nm"])

            if not (
                MIN_WAVELENGTH_NM
                <= wavelength_nm
                <= MAX_WAVELENGTH_NM
            ):
                continue

            if source_row["permitted_use"] != "absorption_only":
                raise ValueError(
                    "Unexpected permitted_use value in absorption data"
                )

            if not source_row["temperature_C"].startswith("23"):
                raise ValueError(
                    "Unexpected temperature metadata in absorption data"
                )

            rows.append(
                {
                    "wavelength_nm": wavelength_nm,
                    "absorption_per_m": float(
                        source_row["absorption_per_m"]
                    ),
                    "absorption_uncertainty_per_m": float(
                        source_row["uncertainty_per_m"]
                    ),
                }
            )

    expected_wavelengths = [
        float(wavelength)
        for wavelength in range(
            MIN_WAVELENGTH_NM,
            MAX_WAVELENGTH_NM + 1,
            WAVELENGTH_STEP_NM,
        )
    ]

    measured_wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    if measured_wavelengths != expected_wavelengths:
        raise ValueError(
            "Absorption wavelengths do not match the expected "
            "350–550 nm grid at 2 nm intervals"
        )

    return rows


def calculate_total_attenuation(
    absorption_rows: list[dict[str, float]],
) -> list[dict[str, float]]:
    """Calculate scattering and total beam attenuation."""

    combined_rows: list[dict[str, float]] = []

    for row in absorption_rows:
        wavelength_nm = row["wavelength_nm"]
        absorption = row["absorption_per_m"]

        scattering = molecular_scattering_coefficient(
            wavelength_nm,
            TEMPERATURE_C,
            DEPOLARIZATION_RATIO,
        )

        attenuation = absorption + scattering

        combined_rows.append(
            {
                "wavelength_nm": wavelength_nm,
                "absorption_per_m": absorption,
                "absorption_uncertainty_per_m": (
                    row["absorption_uncertainty_per_m"]
                ),
                "molecular_scattering_per_m": scattering,
                "attenuation_per_m": attenuation,
                "absorption_fraction": absorption / attenuation,
                "scattering_fraction": scattering / attenuation,
                "model_temperature_c": TEMPERATURE_C,
                "depolarization_ratio": DEPOLARIZATION_RATIO,
            }
        )

    return combined_rows


def write_results_csv(
    rows: list[dict[str, float]],
) -> None:
    """Write the combined spectral coefficients to CSV."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "wavelength_nm",
        "absorption_per_m",
        "absorption_uncertainty_per_m",
        "molecular_scattering_per_m",
        "attenuation_per_m",
        "absorption_fraction",
        "scattering_fraction",
        "model_temperature_c",
        "depolarization_ratio",
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
            writer.writerow(
                {
                    "wavelength_nm": (
                        f"{row['wavelength_nm']:.1f}"
                    ),
                    "absorption_per_m": (
                        f"{row['absorption_per_m']:.12e}"
                    ),
                    "absorption_uncertainty_per_m": (
                        f"{row['absorption_uncertainty_per_m']:.12e}"
                    ),
                    "molecular_scattering_per_m": (
                        f"{row['molecular_scattering_per_m']:.12e}"
                    ),
                    "attenuation_per_m": (
                        f"{row['attenuation_per_m']:.12e}"
                    ),
                    "absorption_fraction": (
                        f"{row['absorption_fraction']:.9f}"
                    ),
                    "scattering_fraction": (
                        f"{row['scattering_fraction']:.9f}"
                    ),
                    "model_temperature_c": (
                        f"{row['model_temperature_c']:.1f}"
                    ),
                    "depolarization_ratio": (
                        f"{row['depolarization_ratio']:.3f}"
                    ),
                }
            )


def create_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot absorption, scattering, and total attenuation."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    absorption = [
        row["absorption_per_m"]
        for row in rows
    ]

    uncertainty = [
        row["absorption_uncertainty_per_m"]
        for row in rows
    ]

    scattering = [
        row["molecular_scattering_per_m"]
        for row in rows
    ]

    attenuation = [
        row["attenuation_per_m"]
        for row in rows
    ]

    lower_absorption = [
        max(value - error, 1.0e-12)
        for value, error in zip(
            absorption,
            uncertainty,
            strict=True,
        )
    ]

    upper_absorption = [
        value + error
        for value, error in zip(
            absorption,
            uncertainty,
            strict=True,
        )
    ]

    minimum_row = min(
        rows,
        key=lambda row: row["attenuation_per_m"],
    )

    figure, axis = plt.subplots(figsize=(8.5, 5.5))

    axis.plot(
        wavelengths,
        absorption,
        linewidth=2.0,
        label="Measured absorption, a",
    )

    axis.fill_between(
        wavelengths,
        lower_absorption,
        upper_absorption,
        alpha=0.2,
        label="Reported absorption uncertainty",
    )

    axis.plot(
        wavelengths,
        scattering,
        linewidth=2.0,
        label="Modelled molecular scattering, b",
    )

    axis.plot(
        wavelengths,
        attenuation,
        linewidth=2.5,
        label="Total beam attenuation, c = a + b",
    )

    axis.axvline(
        minimum_row["wavelength_nm"],
        linestyle="--",
        linewidth=1.0,
    )

    axis.annotate(
        (
            f"Minimum c\n"
            f"{minimum_row['wavelength_nm']:.0f} nm\n"
            f"{minimum_row['attenuation_per_m']:.4e} m$^{{-1}}$"
        ),
        xy=(
            minimum_row["wavelength_nm"],
            minimum_row["attenuation_per_m"],
        ),
        xytext=(15, 25),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    axis.set_yscale("log")

    axis.set_xlabel("Wavelength (nm)")
    axis.set_ylabel("Spectral coefficient (m$^{-1}$)")

    axis.set_title(
        "Pure-water absorption, scattering, and attenuation\n"
        f"{TEMPERATURE_C:.0f} °C, "
        f"depolarization ratio = {DEPOLARIZATION_RATIO:.3f}"
    )

    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        OUTPUT_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    rows: list[dict[str, float]],
) -> None:
    """Print the key combined-spectrum results."""

    minimum_row = min(
        rows,
        key=lambda row: row["attenuation_per_m"],
    )

    print()
    print("Combined pure-water spectral attenuation")
    print("----------------------------------------")
    print(f"Number of wavelengths: {len(rows)}")

    print(
        "Wavelength range: "
        f"{rows[0]['wavelength_nm']:.0f}–"
        f"{rows[-1]['wavelength_nm']:.0f} nm"
    )

    print(f"Model temperature: {TEMPERATURE_C:.1f} °C")

    print(
        "Depolarization ratio: "
        f"{DEPOLARIZATION_RATIO:.3f}"
    )

    print()
    print("Minimum total attenuation")

    print(
        "Wavelength: "
        f"{minimum_row['wavelength_nm']:.0f} nm"
    )

    print(
        "Absorption: "
        f"{minimum_row['absorption_per_m']:.6e} m^-1"
    )

    print(
        "Scattering: "
        f"{minimum_row['molecular_scattering_per_m']:.6e} m^-1"
    )

    print(
        "Total attenuation: "
        f"{minimum_row['attenuation_per_m']:.6e} m^-1"
    )

    print(
        "Scattering contribution: "
        f"{minimum_row['scattering_fraction'] * 100.0:.2f} %"
    )

    print()
    print(
        "Note: the CSV preserves the source-reported absorption "
        "uncertainty. Uncertainty in the scattering model has not "
        "yet been propagated into total attenuation."
    )

    print()
    print(f"Saved data: {OUTPUT_CSV_PATH}")
    print(f"Saved figure: {OUTPUT_FIGURE_PATH}")


def main() -> None:
    """Run the combined absorption-and-scattering analysis."""

    absorption_rows = load_absorption_data()

    combined_rows = calculate_total_attenuation(
        absorption_rows
    )

    write_results_csv(combined_rows)
    create_figure(combined_rows)
    print_summary(combined_rows)


if __name__ == "__main__":
    main()