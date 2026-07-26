"""Analyse the wavelength-dependent molecular scattering of pure water."""

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
    volume_scattering_90,
)


TEMPERATURE_C = 20.0
DEPOLARIZATION_RATIO = 0.039

MIN_WAVELENGTH_NM = 350
MAX_WAVELENGTH_NM = 700
WAVELENGTH_STEP_NM = 1

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

SPECTRUM_CSV_PATH = (
    RESULTS_DIR / "pure_water_scattering_spectrum.csv"
)

VALIDATION_CSV_PATH = (
    RESULTS_DIR / "pure_water_scattering_validation.csv"
)

FIGURE_PATH = (
    FIGURES_DIR / "pure_water_scattering_spectrum.png"
)


# Morel measurements reproduced in Zhang and Hu (2009).
# Values represent beta(90) in m^-1 sr^-1.
MOREL_REFERENCE_VALUES = {
    366.0: 4.53e-4,
    405.0: 2.90e-4,
    436.0: 2.12e-4,
    546.0: 0.835e-4,
    578.0: 0.660e-4,
}


def calculate_spectrum() -> list[dict[str, float]]:
    """Calculate beta(90) and total molecular scattering."""

    rows: list[dict[str, float]] = []

    for wavelength_nm in range(
        MIN_WAVELENGTH_NM,
        MAX_WAVELENGTH_NM + 1,
        WAVELENGTH_STEP_NM,
    ):
        wavelength = float(wavelength_nm)

        beta_90 = volume_scattering_90(
            wavelength,
            TEMPERATURE_C,
            DEPOLARIZATION_RATIO,
        )

        scattering_coefficient = molecular_scattering_coefficient(
            wavelength,
            TEMPERATURE_C,
            DEPOLARIZATION_RATIO,
        )

        rows.append(
            {
                "wavelength_nm": wavelength,
                "temperature_c": TEMPERATURE_C,
                "depolarization_ratio": DEPOLARIZATION_RATIO,
                "beta_90_per_m_sr": beta_90,
                "scattering_coefficient_per_m": scattering_coefficient,
            }
        )

    return rows


def write_spectrum_csv(
    rows: list[dict[str, float]],
) -> None:
    """Write the calculated scattering spectrum to CSV."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "wavelength_nm",
        "temperature_c",
        "depolarization_ratio",
        "beta_90_per_m_sr",
        "scattering_coefficient_per_m",
    ]

    with SPECTRUM_CSV_PATH.open(
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
                    "wavelength_nm": f"{row['wavelength_nm']:.1f}",
                    "temperature_c": f"{row['temperature_c']:.1f}",
                    "depolarization_ratio": (
                        f"{row['depolarization_ratio']:.3f}"
                    ),
                    "beta_90_per_m_sr": (
                        f"{row['beta_90_per_m_sr']:.12e}"
                    ),
                    "scattering_coefficient_per_m": (
                        f"{row['scattering_coefficient_per_m']:.12e}"
                    ),
                }
            )


def calculate_validation() -> list[dict[str, float]]:
    """Compare the model against the Morel measurements."""

    rows: list[dict[str, float]] = []

    for wavelength_nm, measured_value in MOREL_REFERENCE_VALUES.items():
        model_value = volume_scattering_90(
            wavelength_nm,
            TEMPERATURE_C,
            DEPOLARIZATION_RATIO,
        )

        relative_error_percent = (
            (model_value - measured_value)
            / measured_value
            * 100.0
        )

        rows.append(
            {
                "wavelength_nm": wavelength_nm,
                "measured_beta_90_per_m_sr": measured_value,
                "model_beta_90_per_m_sr": model_value,
                "relative_error_percent": relative_error_percent,
                "absolute_relative_error_percent": abs(
                    relative_error_percent
                ),
            }
        )

    return rows


def write_validation_csv(
    rows: list[dict[str, float]],
) -> None:
    """Write the Morel validation results to CSV."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "wavelength_nm",
        "measured_beta_90_per_m_sr",
        "model_beta_90_per_m_sr",
        "relative_error_percent",
        "absolute_relative_error_percent",
    ]

    with VALIDATION_CSV_PATH.open(
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
                    "wavelength_nm": f"{row['wavelength_nm']:.1f}",
                    "measured_beta_90_per_m_sr": (
                        f"{row['measured_beta_90_per_m_sr']:.12e}"
                    ),
                    "model_beta_90_per_m_sr": (
                        f"{row['model_beta_90_per_m_sr']:.12e}"
                    ),
                    "relative_error_percent": (
                        f"{row['relative_error_percent']:.6f}"
                    ),
                    "absolute_relative_error_percent": (
                        f"{row['absolute_relative_error_percent']:.6f}"
                    ),
                }
            )


def create_spectrum_figure(
    rows: list[dict[str, float]],
) -> None:
    """Create the pure-water scattering spectrum figure."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    scattering_coefficients = [
        row["scattering_coefficient_per_m"]
        for row in rows
    ]

    figure, axis = plt.subplots(figsize=(8.0, 5.0))

    axis.plot(
        wavelengths,
        scattering_coefficients,
        linewidth=2.0,
    )

    axis.set_xlabel("Wavelength (nm)")
    axis.set_ylabel(
        "Molecular scattering coefficient, b (m$^{-1}$)"
    )

    axis.set_title(
        "Pure-water molecular scattering spectrum\n"
        f"{TEMPERATURE_C:.0f} °C, "
        f"depolarization ratio = {DEPOLARIZATION_RATIO:.3f}"
    )

    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )

    figure.tight_layout()

    figure.savefig(
        FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_validation_summary(
    rows: list[dict[str, float]],
) -> None:
    """Print the validation results to the terminal."""

    print()
    print("Pure-water scattering validation")
    print(
        f"Temperature: {TEMPERATURE_C:.1f} °C | "
        f"Depolarization ratio: {DEPOLARIZATION_RATIO:.3f}"
    )
    print()

    print(
        f"{'Wavelength':>12} "
        f"{'Measured beta(90)':>20} "
        f"{'Model beta(90)':>20} "
        f"{'Error':>12}"
    )

    print("-" * 70)

    for row in rows:
        print(
            f"{row['wavelength_nm']:>10.0f} nm "
            f"{row['measured_beta_90_per_m_sr']:>20.6e} "
            f"{row['model_beta_90_per_m_sr']:>20.6e} "
            f"{row['relative_error_percent']:>10.3f} %"
        )

    maximum_error = max(
        row["absolute_relative_error_percent"]
        for row in rows
    )

    print()
    print(
        "Maximum absolute relative error: "
        f"{maximum_error:.3f} %"
    )

    if maximum_error > 2.0:
        raise RuntimeError(
            "The model differs from the reference measurements "
            "by more than 2%."
        )


def main() -> None:
    """Run the pure-water scattering analysis."""

    spectrum_rows = calculate_spectrum()
    validation_rows = calculate_validation()

    write_spectrum_csv(spectrum_rows)
    write_validation_csv(validation_rows)
    create_spectrum_figure(spectrum_rows)
    print_validation_summary(validation_rows)

    print()
    print(f"Saved spectrum data: {SPECTRUM_CSV_PATH}")
    print(f"Saved validation data: {VALIDATION_CSV_PATH}")
    print(f"Saved figure: {FIGURE_PATH}")


if __name__ == "__main__":
    main()