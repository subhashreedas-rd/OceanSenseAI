from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from src.propagation import (
    calculate_loss_db,
    calculate_transmittance,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PARAMETER_PATH = (
    PROJECT_ROOT
    / "database"
    / "model_parameters"
    / "wang_2021_water_types.csv"
)

RESULTS_DIR = PROJECT_ROOT / "studies" / "study_01" / "results"
FIGURES_DIR = PROJECT_ROOT / "figures" / "study_01"


def load_approved_parameters(
    path: Path = PARAMETER_PATH,
) -> list[dict[str, str]]:
    """Load parameter records approved for simulation."""

    with path.open("r", encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))

    approved_records = [
        record
        for record in records
        if record["quality_flag"] == "consistent"
        and record["permitted_use"] == "simulation"
    ]

    if not approved_records:
        raise ValueError("No approved simulation parameters were found.")

    return approved_records


def generate_comparison(
    records: list[dict[str, str]],
    maximum_distance_m: int = 50,
) -> list[dict[str, float | str]]:
    """Calculate transmittance and path loss for each water type."""

    if maximum_distance_m <= 0:
        raise ValueError("Maximum distance must be greater than zero.")

    results: list[dict[str, float | str]] = []

    for record in records:
        absorption = float(record["absorption_per_m"])
        scattering = float(record["scattering_per_m"])
        attenuation = absorption + scattering

        for distance_m in range(maximum_distance_m + 1):
            transmittance = calculate_transmittance(
                attenuation_per_m=attenuation,
                distance_m=float(distance_m),
            )

            path_loss_db = calculate_loss_db(transmittance)

            results.append(
                {
                    "record_id": record["record_id"],
                    "water_type": record["water_type"],
                    "absorption_per_m": absorption,
                    "scattering_per_m": scattering,
                    "attenuation_per_m": attenuation,
                    "distance_m": float(distance_m),
                    "transmittance": transmittance,
                    "path_loss_db": path_loss_db,
                }
            )

    return results


def save_results(
    results: list[dict[str, float | str]],
) -> Path:
    """Save the water-type comparison results."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "water_type_comparison.csv"

    fieldnames = [
        "record_id",
        "water_type",
        "absorption_per_m",
        "scattering_per_m",
        "attenuation_per_m",
        "distance_m",
        "transmittance",
        "path_loss_db",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return output_path


def create_figure(
    records: list[dict[str, str]],
    maximum_distance_m: int = 50,
) -> Path:
    """Plot direct-path loss for the approved water types."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURES_DIR / "water_type_comparison.png"

    distances = list(range(maximum_distance_m + 1))

    plt.figure(figsize=(7.5, 4.8))

    for record in records:
        attenuation = (
            float(record["absorption_per_m"])
            + float(record["scattering_per_m"])
        )

        path_losses = []

        for distance_m in distances:
            transmittance = calculate_transmittance(
                attenuation_per_m=attenuation,
                distance_m=float(distance_m),
            )

            path_losses.append(calculate_loss_db(transmittance))

        label = record["water_type"].replace("_", " ").title()

        plt.plot(
            distances,
            path_losses,
            linewidth=2,
            label=f"{label} (c = {attenuation:.3f} m^-1)",
        )

    plt.xlabel("Propagation distance (m)")
    plt.ylabel("Direct-path loss (dB)")
    plt.title("Direct-path loss across water types")
    plt.xlim(0, maximum_distance_m)
    plt.ylim(bottom=0)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()

    return figure_path


def print_selected_results(
    records: list[dict[str, str]],
) -> None:
    """Print transmittance and path loss at selected distances."""

    for record in records:
        attenuation = (
            float(record["absorption_per_m"])
            + float(record["scattering_per_m"])
        )

        water_type = record["water_type"].replace("_", " ").title()

        print(f"\n{water_type} | c = {attenuation:.3f} m^-1")

        for distance_m in (5, 10, 20, 50):
            transmittance = calculate_transmittance(
                attenuation_per_m=attenuation,
                distance_m=float(distance_m),
            )

            path_loss_db = calculate_loss_db(transmittance)

            print(
                f"{distance_m:>2} m: "
                f"T = {transmittance:.6e}, "
                f"loss = {path_loss_db:.2f} dB"
            )


def main() -> None:
    records = load_approved_parameters()

    results = generate_comparison(
        records=records,
        maximum_distance_m=50,
    )

    results_path = save_results(results)

    figure_path = create_figure(
        records=records,
        maximum_distance_m=50,
    )

    print_selected_results(records)

    print(f"\nResults saved to: {results_path}")
    print(f"Figure saved to: {figure_path}")


if __name__ == "__main__":
    main()