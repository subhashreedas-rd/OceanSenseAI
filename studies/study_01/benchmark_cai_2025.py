"""Benchmark the pure-water attenuation model against Cai et al. (2025)."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_CSV_PATH = (
    ROOT_DIR
    / "studies"
    / "study_01"
    / "results"
    / "pure_water_total_attenuation_spectrum.csv"
)

BENCHMARK_CSV_PATH = (
    ROOT_DIR
    / "database"
    / "experimental_benchmarks"
    / "cai_2025_ultrapure_water_532nm.csv"
)

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

OUTPUT_CSV_PATH = (
    RESULTS_DIR
    / "cai_2025_ultrapure_water_532nm_benchmark.csv"
)

FIGURE_PATH = (
    FIGURES_DIR
    / "cai_2025_ultrapure_water_532nm_benchmark.png"
)

TARGET_WAVELENGTH_NM = 532.0


def load_model_value() -> dict[str, float]:
    """Load the OceanSenseAI result at 532 nm."""

    required_columns = {
        "wavelength_nm",
        "absorption_per_m",
        "molecular_scattering_per_m",
        "attenuation_per_m",
    }

    with MODEL_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Model CSV does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Model CSV is missing columns: {missing}"
            )

        matching_rows = []

        for row in reader:
            wavelength_nm = float(row["wavelength_nm"])

            if math.isclose(
                wavelength_nm,
                TARGET_WAVELENGTH_NM,
                rel_tol=0.0,
                abs_tol=1.0e-9,
            ):
                matching_rows.append(
                    {
                        "wavelength_nm": wavelength_nm,
                        "absorption_per_m": float(
                            row["absorption_per_m"]
                        ),
                        "scattering_per_m": float(
                            row["molecular_scattering_per_m"]
                        ),
                        "attenuation_per_m": float(
                            row["attenuation_per_m"]
                        ),
                    }
                )

    if len(matching_rows) != 1:
        raise ValueError(
            "Expected exactly one model row at 532 nm"
        )

    model_row = matching_rows[0]

    expected_attenuation = (
        model_row["absorption_per_m"]
        + model_row["scattering_per_m"]
    )

    if not math.isclose(
        model_row["attenuation_per_m"],
        expected_attenuation,
        rel_tol=1.0e-10,
        abs_tol=1.0e-12,
    ):
        raise ValueError(
            "Model attenuation does not equal absorption "
            "plus scattering"
        )

    return model_row


def load_benchmark_value() -> dict[str, str | float]:
    """Load and validate the Cai et al. benchmark."""

    required_columns = {
        "benchmark_id",
        "source",
        "doi",
        "year",
        "medium",
        "wavelength_nm",
        "quantity_symbol",
        "quantity_name",
        "value_per_m",
        "measurement_method",
        "source_location",
        "source_role",
        "permitted_use",
        "notes",
    }

    with BENCHMARK_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Benchmark CSV does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Benchmark CSV is missing columns: {missing}"
            )

        rows = list(reader)

    if len(rows) != 1:
        raise ValueError(
            "Expected exactly one benchmark row"
        )

    row = rows[0]

    wavelength_nm = float(row["wavelength_nm"])
    measured_value = float(row["value_per_m"])

    if not math.isclose(
        wavelength_nm,
        TARGET_WAVELENGTH_NM,
        rel_tol=0.0,
        abs_tol=1.0e-9,
    ):
        raise ValueError(
            "Benchmark wavelength must be 532 nm"
        )

    if row["quantity_symbol"].strip().lower() != "c":
        raise ValueError(
            "Benchmark quantity must be total attenuation c"
        )

    if measured_value <= 0.0:
        raise ValueError(
            "Benchmark attenuation must be positive"
        )

    return {
        **row,
        "wavelength_nm": wavelength_nm,
        "value_per_m": measured_value,
    }


def calculate_comparison(
    model_row: dict[str, float],
    benchmark_row: dict[str, str | float],
) -> dict[str, float]:
    """Calculate the model–measurement difference."""

    model_value = model_row["attenuation_per_m"]
    measured_value = float(benchmark_row["value_per_m"])

    absolute_difference = model_value - measured_value

    absolute_relative_difference = (
        abs(absolute_difference) / measured_value
    )

    signed_relative_difference = (
        absolute_difference / measured_value
    )

    ratio = model_value / measured_value

    return {
        "wavelength_nm": TARGET_WAVELENGTH_NM,
        "model_absorption_per_m": (
            model_row["absorption_per_m"]
        ),
        "model_scattering_per_m": (
            model_row["scattering_per_m"]
        ),
        "model_attenuation_per_m": model_value,
        "measured_attenuation_per_m": measured_value,
        "difference_per_m": absolute_difference,
        "signed_relative_difference": (
            signed_relative_difference
        ),
        "absolute_relative_difference": (
            absolute_relative_difference
        ),
        "model_to_measurement_ratio": ratio,
    }


def write_results(
    comparison: dict[str, float],
    benchmark_row: dict[str, str | float],
) -> None:
    """Write the benchmark comparison to CSV."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "benchmark_id",
        "source",
        "doi",
        "year",
        "medium",
        "wavelength_nm",
        "model_absorption_per_m",
        "model_scattering_per_m",
        "model_attenuation_per_m",
        "measured_attenuation_per_m",
        "difference_per_m",
        "signed_relative_difference",
        "absolute_relative_difference",
        "model_to_measurement_ratio",
        "measurement_method",
        "source_location",
        "benchmark_scope",
        "benchmark_uncertainty_reported",
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

        writer.writerow(
            {
                "benchmark_id": benchmark_row["benchmark_id"],
                "source": benchmark_row["source"],
                "doi": benchmark_row["doi"],
                "year": benchmark_row["year"],
                "medium": benchmark_row["medium"],
                "wavelength_nm": (
                    f"{comparison['wavelength_nm']:.1f}"
                ),
                "model_absorption_per_m": (
                    f"{comparison['model_absorption_per_m']:.12e}"
                ),
                "model_scattering_per_m": (
                    f"{comparison['model_scattering_per_m']:.12e}"
                ),
                "model_attenuation_per_m": (
                    f"{comparison['model_attenuation_per_m']:.12e}"
                ),
                "measured_attenuation_per_m": (
                    f"{comparison['measured_attenuation_per_m']:.12e}"
                ),
                "difference_per_m": (
                    f"{comparison['difference_per_m']:.12e}"
                ),
                "signed_relative_difference": (
                    f"{comparison['signed_relative_difference']:.9f}"
                ),
                "absolute_relative_difference": (
                    f"{comparison['absolute_relative_difference']:.9f}"
                ),
                "model_to_measurement_ratio": (
                    f"{comparison['model_to_measurement_ratio']:.9f}"
                ),
                "measurement_method": (
                    benchmark_row["measurement_method"]
                ),
                "source_location": (
                    benchmark_row["source_location"]
                ),
                "benchmark_scope": (
                    "single_wavelength_total_attenuation"
                ),
                "benchmark_uncertainty_reported": "no",
            }
        )


def create_figure(
    comparison: dict[str, float],
) -> None:
    """Create a model-versus-measurement comparison figure."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    labels = [
        "OceanSenseAI\nmodel",
        "Cai et al. (2025)\nmeasurement",
    ]

    values = [
        comparison["model_attenuation_per_m"],
        comparison["measured_attenuation_per_m"],
    ]

    figure, axis = plt.subplots(figsize=(7.5, 5.5))

    bars = axis.bar(
        labels,
        values,
    )

    axis.set_ylabel(
        "Beam attenuation coefficient (m$^{-1}$)"
    )

    axis.set_title(
        "Ultrapure-water attenuation benchmark at 532 nm"
    )

    axis.grid(
        axis="y",
        alpha=0.3,
    )

    maximum_value = max(values)

    axis.set_ylim(
        0.0,
        maximum_value * 1.18,
    )

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + maximum_value * 0.02,
            f"{value:.5f}",
            ha="center",
            va="bottom",
        )

    axis.text(
        0.5,
        maximum_value * 1.10,
        (
            "Absolute relative difference: "
            f"{comparison['absolute_relative_difference'] * 100.0:.2f}%"
        ),
        ha="center",
        va="center",
    )

    figure.tight_layout()

    figure.savefig(
        FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    comparison: dict[str, float],
) -> None:
    """Print the main benchmark results."""

    print()
    print("Cai et al. (2025) attenuation benchmark")
    print("-----------------------------------------")

    print(
        f"Wavelength: "
        f"{comparison['wavelength_nm']:.0f} nm"
    )

    print()
    print(
        "OceanSenseAI absorption: "
        f"{comparison['model_absorption_per_m']:.6f} m^-1"
    )

    print(
        "OceanSenseAI molecular scattering: "
        f"{comparison['model_scattering_per_m']:.6f} m^-1"
    )

    print(
        "OceanSenseAI total attenuation: "
        f"{comparison['model_attenuation_per_m']:.6f} m^-1"
    )

    print(
        "Cai et al. measured attenuation: "
        f"{comparison['measured_attenuation_per_m']:.6f} m^-1"
    )

    print()
    print(
        "Signed difference: "
        f"{comparison['difference_per_m']:.6e} m^-1"
    )

    print(
        "Signed relative difference: "
        f"{comparison['signed_relative_difference'] * 100.0:.3f} %"
    )

    print(
        "Absolute relative difference: "
        f"{comparison['absolute_relative_difference'] * 100.0:.3f} %"
    )

    print()
    print(
        "Important: this is a single-wavelength comparison. "
        "The published benchmark does not report uncertainty "
        "for the 532 nm value."
    )

    print()
    print(f"Saved benchmark data: {OUTPUT_CSV_PATH}")
    print(f"Saved benchmark figure: {FIGURE_PATH}")


def main() -> None:
    """Run the Cai et al. benchmark analysis."""

    model_row = load_model_value()
    benchmark_row = load_benchmark_value()

    comparison = calculate_comparison(
        model_row,
        benchmark_row,
    )

    write_results(
        comparison,
        benchmark_row,
    )

    create_figure(comparison)
    print_summary(comparison)


if __name__ == "__main__":
    main()