from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from src.propagation import (
    calculate_loss_db,
    calculate_transmittance,
    load_benchmark,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "studies" / "study_01" / "results"
FIGURES_DIR = PROJECT_ROOT / "figures" / "study_01"


def generate_distance_sweep(
    attenuation_per_m: float,
    maximum_distance_m: int = 50,
) -> list[dict[str, float]]:
    """Calculate transmission from zero to the selected maximum distance."""

    if maximum_distance_m <= 0:
        raise ValueError("Maximum distance must be greater than zero.")

    results = []

    for distance_m in range(maximum_distance_m + 1):
        transmittance = calculate_transmittance(
            attenuation_per_m=attenuation_per_m,
            distance_m=float(distance_m),
        )

        results.append(
            {
                "distance_m": float(distance_m),
                "transmittance": transmittance,
                "received_power_percent": 100.0 * transmittance,
                "path_loss_db": calculate_loss_db(transmittance),
            }
        )

    return results


def save_results(
    results: list[dict[str, float]],
    dataset_id: str,
    wavelength_nm: float,
    attenuation_per_m: float,
) -> Path:
    """Save the distance-sweep results as a CSV file."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / "distance_sweep.csv"

    fieldnames = [
        "dataset_id",
        "wavelength_nm",
        "attenuation_per_m",
        "distance_m",
        "transmittance",
        "received_power_percent",
        "path_loss_db",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "dataset_id": dataset_id,
                    "wavelength_nm": wavelength_nm,
                    "attenuation_per_m": attenuation_per_m,
                    **result,
                }
            )

    return output_path


def create_figure(
    results: list[dict[str, float]],
    wavelength_nm: float,
) -> Path:
    """Plot channel transmittance against propagation distance."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURES_DIR / "transmittance_vs_distance.png"

    distances = [result["distance_m"] for result in results]
    transmittances = [result["transmittance"] for result in results]

    plt.figure(figsize=(7, 4.5))
    plt.plot(distances, transmittances, linewidth=2)
    plt.xlabel("Propagation distance (m)")
    plt.ylabel("Channel transmittance")
    plt.title(f"Direct-path transmittance at {wavelength_nm:.0f} nm")
    plt.xlim(0, max(distances))
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figure_path, dpi=300)
    plt.close()

    return figure_path


def main() -> None:
    benchmark = load_benchmark()

    dataset_id = benchmark["dataset_id"]
    wavelength_nm = float(benchmark["wavelength_nm"])
    attenuation_per_m = float(benchmark["attenuation_per_m"])

    results = generate_distance_sweep(
        attenuation_per_m=attenuation_per_m,
        maximum_distance_m=50,
    )

    results_path = save_results(
        results=results,
        dataset_id=dataset_id,
        wavelength_nm=wavelength_nm,
        attenuation_per_m=attenuation_per_m,
    )

    figure_path = create_figure(
        results=results,
        wavelength_nm=wavelength_nm,
    )

    for distance_m in (10, 20, 30, 50):
        result = results[distance_m]

        print(
            f"{distance_m:>2} m: "
            f"T = {result['transmittance']:.4f}, "
            f"received power = {result['received_power_percent']:.2f}%"
        )

    print(f"\nResults saved to: {results_path}")
    print(f"Figure saved to: {figure_path}")


if __name__ == "__main__":
    main()