"""Run the baseline underwater optical photon-budget study.

This study connects the existing classical optical link budget to mean
photon numbers. It does not simulate individual detection events or a
secure communication protocol.

The transmitter, channel, receiver geometry, and electronics parameters
are reused from the Study 02 baseline so that the new results remain
directly traceable to the existing model.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.link_budget import calculate_link_budget  # noqa: E402
from src.photon_budget import (  # noqa: E402
    mean_detected_photons,
    mean_photons_per_bit,
    photon_energy_joule,
)


RESULTS_DIR = ROOT_DIR / "studies" / "study_03" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_03"

OUTPUT_CSV_PATH = RESULTS_DIR / "photon_budget_distance_sweep.csv"

PHOTON_FIGURE_PATH = (
    FIGURES_DIR
    / "mean_photons_per_bit_vs_distance.png"
)


# Exact SI constant.
ELEMENTARY_CHARGE_C = 1.602176634e-19


# Baseline optical-channel condition reused from Study 01.
WAVELENGTH_NM = 416.0
ATTENUATION_PER_M = 7.1351e-3

# Baseline transmitter and receiver assumptions reused from Study 02.
TRANSMITTED_POWER_W = 0.1
INITIAL_BEAM_RADIUS_M = 0.01
DIVERGENCE_HALF_ANGLE_RAD = 5.0e-3
RECEIVER_RADIUS_M = 0.025
SYSTEM_EFFICIENCY = 0.8
RESPONSIVITY_A_PER_W = 0.30

# Background and electronics assumptions reused from Study 02.
BACKGROUND_POWER_W = 1.0e-9
DARK_CURRENT_A = 1.0e-9
BANDWIDTH_HZ = 100.0e6
TEMPERATURE_K = 300.0
LOAD_RESISTANCE_OHM = 1000.0

# Communication assumption reused from the Study 02 waveform analysis.
BIT_RATE_BPS = 20.0e6

# Distance grid.
MINIMUM_DISTANCE_M = 0
MAXIMUM_DISTANCE_M = 800
DISTANCE_STEP_M = 2


def detector_efficiency_from_responsivity(
    responsivity_a_per_w: float,
    wavelength_nm: float,
) -> float:
    """Estimate detector efficiency from optical responsivity.

    For a unity-gain photodetector, responsivity is related to external
    detection efficiency by

        R = efficiency * q / E_photon

    Therefore,

        efficiency = R * E_photon / q

    This relation assumes that one successfully detected photon produces
    one collected electron and that internal detector gain is absent.
    """
    photon_energy_j = photon_energy_joule(wavelength_nm)

    efficiency = (
        responsivity_a_per_w
        * photon_energy_j
        / ELEMENTARY_CHARGE_C
    )

    if not 0.0 <= efficiency <= 1.0:
        raise ValueError(
            "The responsivity and wavelength imply a detector "
            "efficiency outside the physical range from 0 to 1."
        )

    return efficiency


def run_distance_sweep() -> list[dict[str, float]]:
    """Calculate received and detected mean photons per bit."""

    rows: list[dict[str, float]] = []

    detector_efficiency = detector_efficiency_from_responsivity(
        responsivity_a_per_w=RESPONSIVITY_A_PER_W,
        wavelength_nm=WAVELENGTH_NM,
    )

    for distance_m in range(
        MINIMUM_DISTANCE_M,
        MAXIMUM_DISTANCE_M + DISTANCE_STEP_M,
        DISTANCE_STEP_M,
    ):
        link_result = calculate_link_budget(
            transmitted_power_w=TRANSMITTED_POWER_W,
            attenuation_per_m=ATTENUATION_PER_M,
            distance_m=float(distance_m),
            initial_beam_radius_m=INITIAL_BEAM_RADIUS_M,
            divergence_half_angle_rad=(
                DIVERGENCE_HALF_ANGLE_RAD
            ),
            receiver_radius_m=RECEIVER_RADIUS_M,
            system_efficiency=SYSTEM_EFFICIENCY,
            responsivity_a_per_w=RESPONSIVITY_A_PER_W,
            background_power_w=BACKGROUND_POWER_W,
            dark_current_a=DARK_CURRENT_A,
            bandwidth_hz=BANDWIDTH_HZ,
            temperature_k=TEMPERATURE_K,
            load_resistance_ohm=LOAD_RESISTANCE_OHM,
        )

        received_power_w = link_result["received_power_w"]

        mean_received = mean_photons_per_bit(
            received_power_w=received_power_w,
            bit_rate_bps=BIT_RATE_BPS,
            wavelength_nm=WAVELENGTH_NM,
        )

        mean_detected = mean_detected_photons(
            mean_received=mean_received,
            detector_efficiency=detector_efficiency,
        )

        rows.append(
            {
                "distance_m": float(distance_m),
                "received_power_w": received_power_w,
                "photon_energy_j": photon_energy_joule(
                    WAVELENGTH_NM
                ),
                "bit_duration_s": 1.0 / BIT_RATE_BPS,
                "mean_received_photons_per_bit": mean_received,
                "detector_efficiency": detector_efficiency,
                "mean_detected_photons_per_bit": mean_detected,
            }
        )

    return rows


def write_results(
    rows: list[dict[str, float]],
) -> None:
    """Write the distance-sweep results to CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "distance_m",
        "received_power_w",
        "photon_energy_j",
        "bit_duration_s",
        "mean_received_photons_per_bit",
        "detector_efficiency",
        "mean_detected_photons_per_bit",
    ]

    with OUTPUT_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def create_photon_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot mean received and detected photons per bit."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    distances = [
        row["distance_m"]
        for row in rows
    ]
    mean_received = [
        row["mean_received_photons_per_bit"]
        for row in rows
    ]
    mean_detected = [
        row["mean_detected_photons_per_bit"]
        for row in rows
    ]

    figure, axis = plt.subplots(
        figsize=(8.0, 5.0),
    )

    axis.semilogy(
        distances,
        mean_received,
        label="Mean photons reaching detector",
    )
    axis.semilogy(
        distances,
        mean_detected,
        label="Mean detected photons",
    )

    axis.set_xlabel("Distance (m)")
    axis.set_ylabel("Mean photons per bit")
    axis.set_title(
        "Baseline Photon Budget versus Distance"
    )
    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )
    axis.legend()

    figure.tight_layout()
    figure.savefig(
        PHOTON_FIGURE_PATH,
        dpi=300,
    )
    plt.close(figure)


def find_row_at_distance(
    rows: list[dict[str, float]],
    target_distance_m: float,
) -> dict[str, float]:
    """Return the row nearest to a selected distance."""

    return min(
        rows,
        key=lambda row: abs(
            row["distance_m"] - target_distance_m
        ),
    )


def print_summary(
    rows: list[dict[str, float]],
) -> None:
    """Print the main baseline assumptions and selected results."""

    photon_energy_j = photon_energy_joule(
        WAVELENGTH_NM
    )
    bit_duration_s = 1.0 / BIT_RATE_BPS

    detector_efficiency = (
        detector_efficiency_from_responsivity(
            responsivity_a_per_w=RESPONSIVITY_A_PER_W,
            wavelength_nm=WAVELENGTH_NM,
        )
    )

    print("Study 03A — Baseline photon budget")
    print("-----------------------------------")
    print(
        f"Wavelength: {WAVELENGTH_NM:.1f} nm"
    )
    print(
        f"Photon energy: {photon_energy_j:.6e} J"
    )
    print(
        f"Bit rate: {BIT_RATE_BPS:.6e} bit/s"
    )
    print(
        f"Bit duration: {bit_duration_s:.6e} s"
    )
    print(
        "Responsivity-derived detector efficiency: "
        f"{detector_efficiency:.6f}"
    )

    for target_distance_m in (0.0, 442.0, 800.0):
        row = find_row_at_distance(
            rows,
            target_distance_m,
        )

        print()
        print(
            f"Distance: {row['distance_m']:.0f} m"
        )
        print(
            "  Received optical power: "
            f"{row['received_power_w']:.6e} W"
        )
        print(
            "  Mean received photons per bit: "
            f"{row['mean_received_photons_per_bit']:.6e}"
        )
        print(
            "  Mean detected photons per bit: "
            f"{row['mean_detected_photons_per_bit']:.6e}"
        )

    print()
    print(f"Results written to: {OUTPUT_CSV_PATH}")
    print(f"Figure written to: {PHOTON_FIGURE_PATH}")


def main() -> None:
    """Run the complete photon-budget distance study."""

    rows = run_distance_sweep()

    write_results(rows)
    create_photon_figure(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()