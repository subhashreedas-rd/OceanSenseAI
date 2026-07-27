"""Propagate uncertainty through the pure-water transmission model."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_CSV_PATH = (
    ROOT_DIR
    / "studies"
    / "study_01"
    / "results"
    / "pure_water_total_attenuation_spectrum.csv"
)

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

ATTENUATION_OUTPUT_PATH = (
    RESULTS_DIR / "pure_water_attenuation_uncertainty.csv"
)

TRANSMISSION_OUTPUT_PATH = (
    RESULTS_DIR / "pure_water_transmission_uncertainty.csv"
)

ATTENUATION_FIGURE_PATH = (
    FIGURES_DIR / "pure_water_attenuation_uncertainty.png"
)

TRANSMISSION_FIGURE_PATH = (
    FIGURES_DIR
    / "pure_water_transmittance_uncertainty_416nm.png"
)

SCATTERING_RELATIVE_UNCERTAINTY = 0.02

MIN_WAVELENGTH_NM = 350
MAX_WAVELENGTH_NM = 550
WAVELENGTH_STEP_NM = 2

MIN_DISTANCE_M = 0
MAX_DISTANCE_M = 200
DISTANCE_STEP_M = 2

DB_FACTOR = 10.0 / math.log(10.0)


def load_attenuation_data() -> list[dict[str, float]]:
    """Load and validate the combined attenuation dataset."""

    required_columns = {
        "wavelength_nm",
        "absorption_per_m",
        "absorption_uncertainty_per_m",
        "molecular_scattering_per_m",
        "attenuation_per_m",
    }

    with INPUT_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Attenuation CSV does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Attenuation CSV is missing columns: {missing}"
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

            absorption = float(
                source_row["absorption_per_m"]
            )

            absorption_uncertainty = float(
                source_row["absorption_uncertainty_per_m"]
            )

            scattering = float(
                source_row["molecular_scattering_per_m"]
            )

            attenuation = float(
                source_row["attenuation_per_m"]
            )

            if absorption < 0.0:
                raise ValueError(
                    "Absorption coefficients must be non-negative"
                )

            if absorption_uncertainty < 0.0:
                raise ValueError(
                    "Absorption uncertainties must be non-negative"
                )

            if scattering < 0.0:
                raise ValueError(
                    "Scattering coefficients must be non-negative"
                )

            if attenuation <= 0.0:
                raise ValueError(
                    "Attenuation coefficients must be positive"
                )

            expected_attenuation = absorption + scattering

            if not math.isclose(
                attenuation,
                expected_attenuation,
                rel_tol=1.0e-10,
                abs_tol=1.0e-12,
            ):
                raise ValueError(
                    "Attenuation does not equal absorption "
                    "plus scattering"
                )

            rows.append(
                {
                    "wavelength_nm": wavelength_nm,
                    "absorption_per_m": absorption,
                    "absorption_uncertainty_per_m": (
                        absorption_uncertainty
                    ),
                    "scattering_per_m": scattering,
                    "attenuation_per_m": attenuation,
                }
            )

    rows.sort(
        key=lambda row: row["wavelength_nm"]
    )

    expected_wavelengths = [
        float(wavelength)
        for wavelength in range(
            MIN_WAVELENGTH_NM,
            MAX_WAVELENGTH_NM + 1,
            WAVELENGTH_STEP_NM,
        )
    ]

    actual_wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    if actual_wavelengths != expected_wavelengths:
        raise ValueError(
            "Wavelengths do not match the expected "
            "350–550 nm grid at 2 nm intervals"
        )

    return rows


def calculate_attenuation_uncertainty(
    source_rows: list[dict[str, float]],
) -> list[dict[str, float]]:
    """Calculate combined attenuation uncertainty estimates."""

    result_rows: list[dict[str, float]] = []

    for row in source_rows:
        absorption_uncertainty = (
            row["absorption_uncertainty_per_m"]
        )

        scattering_uncertainty = (
            row["scattering_per_m"]
            * SCATTERING_RELATIVE_UNCERTAINTY
        )

        combined_uncertainty = math.sqrt(
            absorption_uncertainty**2
            + scattering_uncertainty**2
        )

        attenuation = row["attenuation_per_m"]

        attenuation_lower = max(
            attenuation - combined_uncertainty,
            0.0,
        )

        attenuation_upper = (
            attenuation + combined_uncertainty
        )

        attenuation_length = 1.0 / attenuation

        attenuation_length_uncertainty = (
            combined_uncertainty
            / attenuation**2
        )

        half_power_distance = (
            math.log(2.0) / attenuation
        )

        half_power_distance_uncertainty = (
            math.log(2.0)
            * combined_uncertainty
            / attenuation**2
        )

        result_rows.append(
            {
                **row,
                "scattering_uncertainty_per_m": (
                    scattering_uncertainty
                ),
                "combined_uncertainty_per_m": (
                    combined_uncertainty
                ),
                "relative_attenuation_uncertainty": (
                    combined_uncertainty / attenuation
                ),
                "attenuation_lower_per_m": (
                    attenuation_lower
                ),
                "attenuation_upper_per_m": (
                    attenuation_upper
                ),
                "attenuation_length_m": (
                    attenuation_length
                ),
                "attenuation_length_uncertainty_m": (
                    attenuation_length_uncertainty
                ),
                "half_power_distance_m": (
                    half_power_distance
                ),
                "half_power_distance_uncertainty_m": (
                    half_power_distance_uncertainty
                ),
            }
        )

    return result_rows


def calculate_transmission_uncertainty(
    attenuation_rows: list[dict[str, float]],
) -> list[dict[str, float]]:
    """Propagate attenuation uncertainty through transmission."""

    result_rows: list[dict[str, float]] = []

    for distance_m in range(
        MIN_DISTANCE_M,
        MAX_DISTANCE_M + 1,
        DISTANCE_STEP_M,
    ):
        distance = float(distance_m)

        for row in attenuation_rows:
            attenuation = row["attenuation_per_m"]

            uncertainty = row[
                "combined_uncertainty_per_m"
            ]

            attenuation_lower = row[
                "attenuation_lower_per_m"
            ]

            attenuation_upper = row[
                "attenuation_upper_per_m"
            ]

            transmittance = math.exp(
                -attenuation * distance
            )

            transmittance_uncertainty = (
                distance
                * transmittance
                * uncertainty
            )

            transmittance_lower = math.exp(
                -attenuation_upper * distance
            )

            transmittance_upper = math.exp(
                -attenuation_lower * distance
            )

            path_loss_db = (
                DB_FACTOR
                * attenuation
                * distance
            )

            path_loss_uncertainty_db = (
                DB_FACTOR
                * uncertainty
                * distance
            )

            path_loss_lower_db = (
                DB_FACTOR
                * attenuation_lower
                * distance
            )

            path_loss_upper_db = (
                DB_FACTOR
                * attenuation_upper
                * distance
            )

            result_rows.append(
                {
                    "distance_m": distance,
                    "wavelength_nm": row["wavelength_nm"],
                    "attenuation_per_m": attenuation,
                    "attenuation_uncertainty_per_m": uncertainty,
                    "transmittance": transmittance,
                    "transmittance_uncertainty": (
                        transmittance_uncertainty
                    ),
                    "transmittance_lower": (
                        transmittance_lower
                    ),
                    "transmittance_upper": (
                        transmittance_upper
                    ),
                    "path_loss_db": path_loss_db,
                    "path_loss_uncertainty_db": (
                        path_loss_uncertainty_db
                    ),
                    "path_loss_lower_db": (
                        path_loss_lower_db
                    ),
                    "path_loss_upper_db": (
                        path_loss_upper_db
                    ),
                }
            )

    return result_rows


def write_attenuation_results(
    rows: list[dict[str, float]],
) -> None:
    """Write wavelength-dependent uncertainty results."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "wavelength_nm",
        "absorption_per_m",
        "absorption_uncertainty_per_m",
        "scattering_per_m",
        "scattering_uncertainty_per_m",
        "attenuation_per_m",
        "combined_uncertainty_per_m",
        "relative_attenuation_uncertainty",
        "attenuation_lower_per_m",
        "attenuation_upper_per_m",
        "attenuation_length_m",
        "attenuation_length_uncertainty_m",
        "half_power_distance_m",
        "half_power_distance_uncertainty_m",
        "scattering_relative_uncertainty_assumption",
    ]

    with ATTENUATION_OUTPUT_PATH.open(
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
                    "scattering_per_m": (
                        f"{row['scattering_per_m']:.12e}"
                    ),
                    "scattering_uncertainty_per_m": (
                        f"{row['scattering_uncertainty_per_m']:.12e}"
                    ),
                    "attenuation_per_m": (
                        f"{row['attenuation_per_m']:.12e}"
                    ),
                    "combined_uncertainty_per_m": (
                        f"{row['combined_uncertainty_per_m']:.12e}"
                    ),
                    "relative_attenuation_uncertainty": (
                        f"{row['relative_attenuation_uncertainty']:.9f}"
                    ),
                    "attenuation_lower_per_m": (
                        f"{row['attenuation_lower_per_m']:.12e}"
                    ),
                    "attenuation_upper_per_m": (
                        f"{row['attenuation_upper_per_m']:.12e}"
                    ),
                    "attenuation_length_m": (
                        f"{row['attenuation_length_m']:.9f}"
                    ),
                    "attenuation_length_uncertainty_m": (
                        f"{row['attenuation_length_uncertainty_m']:.9f}"
                    ),
                    "half_power_distance_m": (
                        f"{row['half_power_distance_m']:.9f}"
                    ),
                    "half_power_distance_uncertainty_m": (
                        f"{row['half_power_distance_uncertainty_m']:.9f}"
                    ),
                    "scattering_relative_uncertainty_assumption": (
                        f"{SCATTERING_RELATIVE_UNCERTAINTY:.6f}"
                    ),
                }
            )


def write_transmission_results(
    rows: list[dict[str, float]],
) -> None:
    """Write wavelength–distance uncertainty results."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "distance_m",
        "wavelength_nm",
        "attenuation_per_m",
        "attenuation_uncertainty_per_m",
        "transmittance",
        "transmittance_uncertainty",
        "transmittance_lower",
        "transmittance_upper",
        "path_loss_db",
        "path_loss_uncertainty_db",
        "path_loss_lower_db",
        "path_loss_upper_db",
    ]

    with TRANSMISSION_OUTPUT_PATH.open(
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
                    "distance_m": (
                        f"{row['distance_m']:.1f}"
                    ),
                    "wavelength_nm": (
                        f"{row['wavelength_nm']:.1f}"
                    ),
                    "attenuation_per_m": (
                        f"{row['attenuation_per_m']:.12e}"
                    ),
                    "attenuation_uncertainty_per_m": (
                        f"{row['attenuation_uncertainty_per_m']:.12e}"
                    ),
                    "transmittance": (
                        f"{row['transmittance']:.12e}"
                    ),
                    "transmittance_uncertainty": (
                        f"{row['transmittance_uncertainty']:.12e}"
                    ),
                    "transmittance_lower": (
                        f"{row['transmittance_lower']:.12e}"
                    ),
                    "transmittance_upper": (
                        f"{row['transmittance_upper']:.12e}"
                    ),
                    "path_loss_db": (
                        f"{row['path_loss_db']:.9f}"
                    ),
                    "path_loss_uncertainty_db": (
                        f"{row['path_loss_uncertainty_db']:.9f}"
                    ),
                    "path_loss_lower_db": (
                        f"{row['path_loss_lower_db']:.9f}"
                    ),
                    "path_loss_upper_db": (
                        f"{row['path_loss_upper_db']:.9f}"
                    ),
                }
            )


def create_attenuation_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot attenuation with combined uncertainty bounds."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    attenuation = [
        row["attenuation_per_m"]
        for row in rows
    ]

    lower = [
        row["attenuation_lower_per_m"]
        for row in rows
    ]

    upper = [
        row["attenuation_upper_per_m"]
        for row in rows
    ]

    minimum_row = min(
        rows,
        key=lambda row: row["attenuation_per_m"],
    )

    figure, axis = plt.subplots(figsize=(8.5, 5.5))

    axis.plot(
        wavelengths,
        attenuation,
        linewidth=2.0,
        label="Total attenuation",
    )

    axis.fill_between(
        wavelengths,
        lower,
        upper,
        alpha=0.25,
        label="Combined uncertainty estimate",
    )

    axis.axvline(
        minimum_row["wavelength_nm"],
        linestyle="--",
        linewidth=1.0,
        label=(
            "Nominal minimum: "
            f"{minimum_row['wavelength_nm']:.0f} nm"
        ),
    )

    axis.set_xlabel("Wavelength (nm)")
    axis.set_ylabel(
        "Beam attenuation coefficient (m$^{-1}$)"
    )

    axis.set_title(
        "Pure-water attenuation uncertainty"
    )

    axis.grid(True, alpha=0.3)
    axis.legend()

    figure.tight_layout()

    figure.savefig(
        ATTENUATION_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_transmission_figure(
    attenuation_rows: list[dict[str, float]],
    transmission_rows: list[dict[str, float]],
) -> None:
    """Plot transmittance uncertainty at the optimum wavelength."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    minimum_row = min(
        attenuation_rows,
        key=lambda row: row["attenuation_per_m"],
    )

    best_wavelength = minimum_row["wavelength_nm"]

    selected_rows = [
        row
        for row in transmission_rows
        if row["wavelength_nm"] == best_wavelength
    ]

    distances = [
        row["distance_m"]
        for row in selected_rows
    ]

    transmittance = [
        row["transmittance"]
        for row in selected_rows
    ]

    lower = [
        row["transmittance_lower"]
        for row in selected_rows
    ]

    upper = [
        row["transmittance_upper"]
        for row in selected_rows
    ]

    figure, axis = plt.subplots(figsize=(8.5, 5.5))

    axis.plot(
        distances,
        transmittance,
        linewidth=2.0,
        label="Nominal transmittance",
    )

    axis.fill_between(
        distances,
        lower,
        upper,
        alpha=0.25,
        label="Combined uncertainty estimate",
    )

    axis.set_xlabel("Propagation distance (m)")
    axis.set_ylabel("Direct-path transmittance")

    axis.set_title(
        "Pure-water transmittance uncertainty\n"
        f"{best_wavelength:.0f} nm"
    )

    axis.set_ylim(0.0, 1.02)
    axis.grid(True, alpha=0.3)
    axis.legend()

    figure.tight_layout()

    figure.savefig(
        TRANSMISSION_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    attenuation_rows: list[dict[str, float]],
    transmission_rows: list[dict[str, float]],
) -> None:
    """Print the main uncertainty results."""

    minimum_row = min(
        attenuation_rows,
        key=lambda row: row["attenuation_per_m"],
    )

    best_wavelength = minimum_row["wavelength_nm"]

    row_100_m = next(
        row
        for row in transmission_rows
        if row["wavelength_nm"] == best_wavelength
        and row["distance_m"] == 100.0
    )

    print()
    print("Pure-water uncertainty analysis")
    print("--------------------------------")
    print(
        "Scattering relative uncertainty assumption: "
        f"{SCATTERING_RELATIVE_UNCERTAINTY * 100.0:.2f} %"
    )

    print()
    print(
        "Nominal minimum-attenuation wavelength: "
        f"{best_wavelength:.0f} nm"
    )

    print(
        "Attenuation coefficient: "
        f"{minimum_row['attenuation_per_m']:.6e} m^-1"
    )

    print(
        "Combined attenuation uncertainty: "
        f"{minimum_row['combined_uncertainty_per_m']:.6e} m^-1"
    )

    print(
        "Relative attenuation uncertainty: "
        f"{minimum_row['relative_attenuation_uncertainty'] * 100.0:.2f} %"
    )

    print()
    print(
        "Attenuation length: "
        f"{minimum_row['attenuation_length_m']:.3f} "
        f"± "
        f"{minimum_row['attenuation_length_uncertainty_m']:.3f} m"
    )

    print(
        "Half-power distance: "
        f"{minimum_row['half_power_distance_m']:.3f} "
        f"± "
        f"{minimum_row['half_power_distance_uncertainty_m']:.3f} m"
    )

    print()
    print("At 100 m:")

    print(
        "Transmittance: "
        f"{row_100_m['transmittance']:.6f} "
        f"± "
        f"{row_100_m['transmittance_uncertainty']:.6f}"
    )

    print(
        "Path loss: "
        f"{row_100_m['path_loss_db']:.3f} "
        f"± "
        f"{row_100_m['path_loss_uncertainty_db']:.3f} dB"
    )

    print()
    print(
        "Important: the 2% scattering uncertainty is an "
        "initial modelling assumption based on the adopted "
        "validation criterion. It is not a source-reported "
        "measurement uncertainty."
    )

    print()
    print(f"Saved attenuation data: {ATTENUATION_OUTPUT_PATH}")
    print(f"Saved transmission data: {TRANSMISSION_OUTPUT_PATH}")
    print(f"Saved attenuation figure: {ATTENUATION_FIGURE_PATH}")
    print(f"Saved transmission figure: {TRANSMISSION_FIGURE_PATH}")


def main() -> None:
    """Run the pure-water uncertainty analysis."""

    source_rows = load_attenuation_data()

    attenuation_rows = calculate_attenuation_uncertainty(
        source_rows
    )

    transmission_rows = calculate_transmission_uncertainty(
        attenuation_rows
    )

    write_attenuation_results(attenuation_rows)
    write_transmission_results(transmission_rows)

    create_attenuation_figure(attenuation_rows)

    create_transmission_figure(
        attenuation_rows,
        transmission_rows,
    )

    print_summary(
        attenuation_rows,
        transmission_rows,
    )


if __name__ == "__main__":
    main()