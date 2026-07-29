"""Run the baseline underwater optical link-budget simulation.

The numerical parameters in this script are explicit baseline assumptions
for software verification and sensitivity analysis. They are not presented
as an experimentally validated or optimised communication system.
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


RESULTS_DIR = ROOT_DIR / "studies" / "study_02" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_02"

OUTPUT_CSV_PATH = RESULTS_DIR / "baseline_link_budget_distance_sweep.csv"

POWER_FIGURE_PATH = (
    FIGURES_DIR
    / "baseline_received_optical_power_vs_distance.png"
)

SNR_FIGURE_PATH = (
    FIGURES_DIR
    / "baseline_snr_vs_distance.png"
)


# Baseline optical-channel condition from Study 01.
WAVELENGTH_NM = 416.0
ATTENUATION_PER_M = 7.1351e-3

# Explicit transmitter and receiver assumptions.
TRANSMITTED_POWER_W = 0.1
INITIAL_BEAM_RADIUS_M = 0.01
DIVERGENCE_HALF_ANGLE_RAD = 5.0e-3
RECEIVER_RADIUS_M = 0.025
SYSTEM_EFFICIENCY = 0.8
RESPONSIVITY_A_PER_W = 0.30

# Explicit background and electronics assumptions.
BACKGROUND_POWER_W = 1.0e-9
DARK_CURRENT_A = 1.0e-9
BANDWIDTH_HZ = 100.0e6
TEMPERATURE_K = 300.0
LOAD_RESISTANCE_OHM = 1000.0

# Simulation grid.
MINIMUM_DISTANCE_M = 0
MAXIMUM_DISTANCE_M = 800
DISTANCE_STEP_M = 2

SNR_THRESHOLDS_DB = (20.0, 10.0, 0.0)


def run_distance_sweep() -> list[dict[str, float]]:
    """Calculate the link budget over the complete distance grid."""

    rows: list[dict[str, float]] = []

    for distance_m in range(
        MINIMUM_DISTANCE_M,
        MAXIMUM_DISTANCE_M + DISTANCE_STEP_M,
        DISTANCE_STEP_M,
    ):
        result = calculate_link_budget(
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

        rows.append(result)

    return rows


def write_results(
    rows: list[dict[str, float]],
) -> None:
    """Write the complete distance sweep to CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "distance_m",
        "beam_radius_m",
        "geometric_collection_efficiency",
        "water_transmittance",
        "received_power_w",
        "signal_current_a",
        "background_current_a",
        "shot_noise_variance_a2",
        "thermal_noise_variance_a2",
        "total_noise_variance_a2",
        "noise_rms_current_a",
        "snr_linear",
        "snr_db",
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
                "distance_m": f"{row['distance_m']:.1f}",
            }

            for fieldname in fieldnames[1:]:
                formatted_row[fieldname] = (
                    f"{row[fieldname]:.12e}"
                )

            writer.writerow(formatted_row)


def create_power_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot received optical power against distance."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    distances = [
        row["distance_m"]
        for row in rows
    ]

    received_powers = [
        row["received_power_w"]
        for row in rows
    ]

    figure, axis = plt.subplots(
        figsize=(9.0, 6.0),
    )

    axis.semilogy(
        distances,
        received_powers,
        linewidth=2.0,
    )

    axis.set_xlabel(
        "Propagation distance (m)"
    )

    axis.set_ylabel(
        "Received optical power (W)"
    )

    axis.set_title(
        "Baseline received optical power versus distance"
    )

    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )

    figure.tight_layout()

    figure.savefig(
        POWER_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_snr_figure(
    rows: list[dict[str, float]],
) -> None:
    """Plot electrical SNR against distance."""

    distances = [
        row["distance_m"]
        for row in rows
    ]

    snr_values_db = [
        row["snr_db"]
        for row in rows
    ]

    figure, axis = plt.subplots(
        figsize=(9.0, 6.0),
    )

    axis.plot(
        distances,
        snr_values_db,
        linewidth=2.0,
        label="Calculated SNR",
    )

    for threshold_db in SNR_THRESHOLDS_DB:
        axis.axhline(
            threshold_db,
            linestyle="--",
            linewidth=1.0,
            label=f"{threshold_db:.0f} dB threshold",
        )

    axis.set_xlabel(
        "Propagation distance (m)"
    )

    axis.set_ylabel(
        "Electrical SNR (dB)"
    )

    axis.set_title(
        "Baseline receiver SNR versus distance"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        SNR_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def maximum_distance_above_threshold(
    rows: list[dict[str, float]],
    threshold_db: float,
) -> float | None:
    """Find the final grid point meeting an SNR threshold."""

    valid_distances = [
        row["distance_m"]
        for row in rows
        if row["snr_db"] >= threshold_db
    ]

    if not valid_distances:
        return None

    return max(valid_distances)


def print_summary(
    rows: list[dict[str, float]],
) -> None:
    """Print the main baseline simulation results."""

    first_row = rows[0]
    final_row = rows[-1]

    print()
    print("Baseline underwater optical link budget")
    print("---------------------------------------")

    print(f"Wavelength: {WAVELENGTH_NM:.0f} nm")

    print(
        "Water attenuation coefficient: "
        f"{ATTENUATION_PER_M:.7f} m^-1"
    )

    print(
        "Transmitted optical power: "
        f"{TRANSMITTED_POWER_W:.3f} W"
    )

    print(
        "Beam divergence half-angle: "
        f"{DIVERGENCE_HALF_ANGLE_RAD * 1000.0:.2f} mrad"
    )

    print(
        "Receiver diameter: "
        f"{2.0 * RECEIVER_RADIUS_M * 100.0:.1f} cm"
    )

    print(
        "Detector responsivity: "
        f"{RESPONSIVITY_A_PER_W:.2f} A/W"
    )

    print(
        "Electrical bandwidth: "
        f"{BANDWIDTH_HZ / 1.0e6:.1f} MHz"
    )

    print()
    print(
        "Received power at 0 m: "
        f"{first_row['received_power_w']:.6e} W"
    )

    print(
        f"Received power at {MAXIMUM_DISTANCE_M} m: "
        f"{final_row['received_power_w']:.6e} W"
    )

    print(
        "SNR at 0 m: "
        f"{first_row['snr_db']:.2f} dB"
    )

    print(
        f"SNR at {MAXIMUM_DISTANCE_M} m: "
        f"{final_row['snr_db']:.2f} dB"
    )

    print()
    print("Grid-limited SNR threshold distances")

    for threshold_db in SNR_THRESHOLDS_DB:
        maximum_distance = (
            maximum_distance_above_threshold(
                rows=rows,
                threshold_db=threshold_db,
            )
        )

        if maximum_distance is None:
            print(
                f"{threshold_db:.0f} dB: "
                "not reached"
            )
        else:
            print(
                f"{threshold_db:.0f} dB: "
                f"{maximum_distance:.0f} m"
            )

    print()
    print(
        "These values use explicit baseline assumptions "
        "and are not validated hardware specifications."
    )

    print()
    print(f"Saved results: {OUTPUT_CSV_PATH}")
    print(f"Saved power figure: {POWER_FIGURE_PATH}")
    print(f"Saved SNR figure: {SNR_FIGURE_PATH}")


def main() -> None:
    """Run the baseline link-budget study."""

    rows = run_distance_sweep()

    write_results(rows)
    create_power_figure(rows)
    create_snr_figure(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()