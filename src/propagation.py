from __future__ import annotations

import csv
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "database"
    / "experimental_benchmarks"
    / "zhang_zhou_2023_attenuation.csv"
)


def calculate_transmittance(
    attenuation_per_m: float,
    distance_m: float,
) -> float:
    """Calculate Beer–Lambert channel transmittance."""

    if attenuation_per_m < 0:
        raise ValueError("Attenuation coefficient cannot be negative.")

    if distance_m < 0:
        raise ValueError("Propagation distance cannot be negative.")

    return math.exp(-attenuation_per_m * distance_m)


def calculate_loss_db(transmittance: float) -> float:
    """Convert channel transmittance to optical loss in decibels."""

    if not 0 < transmittance <= 1:
        raise ValueError("Transmittance must satisfy 0 < T <= 1.")

    return -10.0 * math.log10(transmittance)


def load_benchmark(path: Path = DATA_PATH) -> dict[str, str]:
    """Load the experimental attenuation benchmark."""

    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if len(rows) != 1:
        raise ValueError(
            f"Expected one benchmark row in {path}, found {len(rows)}."
        )

    return rows[0]


def run_verification_checks() -> None:
    """Check basic physical and mathematical behaviour."""

    assert calculate_transmittance(0.1, 0.0) == 1.0
    assert calculate_transmittance(0.0, 100.0) == 1.0

    transmission_5_m = calculate_transmittance(0.1, 5.0)
    transmission_10_m = calculate_transmittance(0.1, 10.0)

    assert transmission_10_m < transmission_5_m
    assert 0.0 < transmission_10_m <= 1.0


def main() -> None:
    benchmark = load_benchmark()

    attenuation_per_m = float(benchmark["attenuation_per_m"])
    attenuation_db_per_m = float(benchmark["attenuation_db_per_m"])
    distance_m = float(benchmark["path_length_m"])

    transmittance = calculate_transmittance(
        attenuation_per_m=attenuation_per_m,
        distance_m=distance_m,
    )

    total_loss_db = calculate_loss_db(transmittance)
    calculated_db_per_m = calculate_loss_db(
        calculate_transmittance(attenuation_per_m, 1.0)
    )

    run_verification_checks()

    if not math.isclose(
        calculated_db_per_m,
        attenuation_db_per_m,
        abs_tol=0.001,
    ):
        raise AssertionError(
            "The attenuation values in m^-1 and dB/m are inconsistent."
        )

    print(f"Dataset: {benchmark['dataset_id']}")
    print(f"Medium: {benchmark['medium']}")
    print(f"Wavelength: {benchmark['wavelength_nm']} nm")
    print(f"Distance: {distance_m:.1f} m")
    print(f"Attenuation coefficient: {attenuation_per_m:.4f} m^-1")
    print(f"Channel transmittance: {transmittance:.6f}")
    print(f"Received power fraction: {100 * transmittance:.2f}%")
    print(f"Total path loss: {total_loss_db:.4f} dB")
    print("Verification checks: passed")


if __name__ == "__main__":
    main()