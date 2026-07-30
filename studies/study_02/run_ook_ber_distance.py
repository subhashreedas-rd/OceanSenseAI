"""Simulate OOK detection and BER over underwater link distance.

This study connects:

    transmitted bits
    -> OOK detector-current levels
    -> underwater optical link budget
    -> receiver noise
    -> threshold detection
    -> recovered bits
    -> measured and theoretical BER

The model uses one detector decision sample per bit. Oversampling,
waveform generation, pulse shaping, and filtering are introduced later.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.link_budget import calculate_link_budget  # noqa: E402
from src.ook import (  # noqa: E402
    generate_bits,
    simulate_ook_detection,
    theoretical_midpoint_ber,
)


RESULTS_DIR = ROOT_DIR / "studies" / "study_02" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_02"

THEORY_OUTPUT_PATH = (
    RESULTS_DIR
    / "ook_theoretical_ber_distance_sweep.csv"
)

SIMULATION_OUTPUT_PATH = (
    RESULTS_DIR
    / "ook_simulated_ber_points.csv"
)

BER_FIGURE_PATH = (
    FIGURES_DIR
    / "ook_ber_vs_distance.png"
)

DETECTION_FIGURE_PATH = (
    FIGURES_DIR
    / "ook_detection_example_442m.png"
)


# Study 01 optical-channel condition.
WAVELENGTH_NM = 416.0
ATTENUATION_PER_M = 7.1351e-3

# Baseline transmitter and receiver assumptions.
TRANSMITTED_POWER_W = 0.1
INITIAL_BEAM_RADIUS_M = 0.01
DIVERGENCE_HALF_ANGLE_RAD = 5.0e-3
RECEIVER_RADIUS_M = 0.025
SYSTEM_EFFICIENCY = 0.8
RESPONSIVITY_A_PER_W = 0.30

# Baseline detector and electronics assumptions.
BACKGROUND_POWER_W = 1.0e-9
DARK_CURRENT_A = 1.0e-9
BANDWIDTH_HZ = 100.0e6
TEMPERATURE_K = 300.0
LOAD_RESISTANCE_OHM = 1000.0

# Distance analysis.
MINIMUM_DISTANCE_M = 0
MAXIMUM_DISTANCE_M = 800
DISTANCE_STEP_M = 2

SIMULATED_DISTANCES_M = (
    400,
    442,
    500,
    544,
    600,
)

NUMBER_OF_BITS = 100_000
BIT_SEQUENCE_SEED = 20260730
NOISE_SEED_BASE = 9000

EXAMPLE_DISTANCE_M = 442
EXAMPLE_NUMBER_OF_BITS = 60

FIGURE_BER_FLOOR = 1.0e-12


def calculate_link_at_distance(
    distance_m: float,
) -> dict[str, float]:
    """Calculate the receiver link budget at one distance."""

    return calculate_link_budget(
        transmitted_power_w=TRANSMITTED_POWER_W,
        attenuation_per_m=ATTENUATION_PER_M,
        distance_m=distance_m,
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


def calculate_theoretical_sweep() -> list[dict[str, float]]:
    """Calculate theoretical OOK BER over the distance grid."""

    rows: list[dict[str, float]] = []

    for distance_m in range(
        MINIMUM_DISTANCE_M,
        MAXIMUM_DISTANCE_M + DISTANCE_STEP_M,
        DISTANCE_STEP_M,
    ):
        link = calculate_link_at_distance(
            distance_m=float(distance_m),
        )

        theoretical_ber = theoretical_midpoint_ber(
            signal_current_a=link["signal_current_a"],
            background_current_a=link[
                "background_current_a"
            ],
            dark_current_a=DARK_CURRENT_A,
            bandwidth_hz=BANDWIDTH_HZ,
            temperature_k=TEMPERATURE_K,
            load_resistance_ohm=LOAD_RESISTANCE_OHM,
        )

        rows.append(
            {
                "distance_m": float(distance_m),
                "received_power_w": link[
                    "received_power_w"
                ],
                "signal_current_a": link[
                    "signal_current_a"
                ],
                "snr_db": link["snr_db"],
                "theoretical_ber": theoretical_ber,
            }
        )

    return rows


def run_simulated_points() -> tuple[
    list[dict[str, float | int]],
    dict[str, float | int | list[int] | list[float]],
]:
    """Run Monte Carlo detection at selected distances."""

    transmitted_bits = generate_bits(
        number_of_bits=NUMBER_OF_BITS,
        seed=BIT_SEQUENCE_SEED,
    )

    simulation_rows: list[
        dict[str, float | int]
    ] = []

    example_result: (
        dict[
            str,
            float | int | list[int] | list[float],
        ]
        | None
    ) = None

    for index, distance_m in enumerate(
        SIMULATED_DISTANCES_M
    ):
        link = calculate_link_at_distance(
            distance_m=float(distance_m),
        )

        result = simulate_ook_detection(
            transmitted_bits=transmitted_bits,
            signal_current_a=link["signal_current_a"],
            background_current_a=link[
                "background_current_a"
            ],
            dark_current_a=DARK_CURRENT_A,
            bandwidth_hz=BANDWIDTH_HZ,
            temperature_k=TEMPERATURE_K,
            load_resistance_ohm=LOAD_RESISTANCE_OHM,
            seed=NOISE_SEED_BASE + index,
        )

        simulation_rows.append(
            {
                "distance_m": float(distance_m),
                "number_of_bits": NUMBER_OF_BITS,
                "error_count": cast(
                    int,
                    result["error_count"],
                ),
                "measured_ber": cast(
                    float,
                    result["ber"],
                ),
                "theoretical_ber": cast(
                    float,
                    result["theoretical_ber"],
                ),
                "snr_db": link["snr_db"],
                "received_power_w": link[
                    "received_power_w"
                ],
                "signal_current_a": link[
                    "signal_current_a"
                ],
            }
        )

        if distance_m == EXAMPLE_DISTANCE_M:
            example_result = result

    if example_result is None:
        raise RuntimeError(
            "Example distance was not simulated"
        )

    return simulation_rows, example_result


def write_theoretical_results(
    rows: list[dict[str, float]],
) -> None:
    """Write theoretical BER distance results."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "distance_m",
        "received_power_w",
        "signal_current_a",
        "snr_db",
        "theoretical_ber",
    ]

    with THEORY_OUTPUT_PATH.open(
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
                    "received_power_w": (
                        f"{row['received_power_w']:.12e}"
                    ),
                    "signal_current_a": (
                        f"{row['signal_current_a']:.12e}"
                    ),
                    "snr_db": (
                        f"{row['snr_db']:.12e}"
                    ),
                    "theoretical_ber": (
                        f"{row['theoretical_ber']:.12e}"
                    ),
                }
            )


def write_simulation_results(
    rows: list[dict[str, float | int]],
) -> None:
    """Write measured BER results at selected distances."""

    fieldnames = [
        "distance_m",
        "number_of_bits",
        "error_count",
        "measured_ber",
        "theoretical_ber",
        "snr_db",
        "received_power_w",
        "signal_current_a",
    ]

    with SIMULATION_OUTPUT_PATH.open(
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
                        f"{float(row['distance_m']):.1f}"
                    ),
                    "number_of_bits": int(
                        row["number_of_bits"]
                    ),
                    "error_count": int(
                        row["error_count"]
                    ),
                    "measured_ber": (
                        f"{float(row['measured_ber']):.12e}"
                    ),
                    "theoretical_ber": (
                        f"{float(row['theoretical_ber']):.12e}"
                    ),
                    "snr_db": (
                        f"{float(row['snr_db']):.12e}"
                    ),
                    "received_power_w": (
                        f"{float(row['received_power_w']):.12e}"
                    ),
                    "signal_current_a": (
                        f"{float(row['signal_current_a']):.12e}"
                    ),
                }
            )


def create_ber_figure(
    theory_rows: list[dict[str, float]],
    simulation_rows: list[
        dict[str, float | int]
    ],
) -> None:
    """Plot theoretical and measured BER against distance."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    theory_distances = [
        row["distance_m"]
        for row in theory_rows
    ]

    theory_ber = [
        max(
            row["theoretical_ber"],
            FIGURE_BER_FLOOR,
        )
        for row in theory_rows
    ]

    simulation_distances = [
        float(row["distance_m"])
        for row in simulation_rows
    ]

    measured_ber = [
        max(
            float(row["measured_ber"]),
            1.0 / NUMBER_OF_BITS,
        )
        for row in simulation_rows
    ]

    figure, axis = plt.subplots(
        figsize=(9.0, 6.0),
    )

    axis.semilogy(
        theory_distances,
        theory_ber,
        linewidth=2.0,
        label="Theoretical midpoint-threshold BER",
    )

    axis.semilogy(
        simulation_distances,
        measured_ber,
        linestyle="none",
        marker="o",
        markersize=7,
        label=(
            f"Simulation ({NUMBER_OF_BITS:,} bits per point)"
        ),
    )

    axis.set_xlabel(
        "Propagation distance (m)"
    )

    axis.set_ylabel(
        "Bit-error rate"
    )

    axis.set_title(
        "OOK bit-error rate versus underwater link distance"
    )

    axis.set_ylim(
        FIGURE_BER_FLOOR,
        1.0,
    )

    axis.grid(
        True,
        which="both",
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        BER_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_detection_figure(
    result: dict[
        str,
        float | int | list[int] | list[float],
    ],
) -> None:
    """Plot noisy decision samples and detected bits."""

    transmitted_bits = cast(
        list[int],
        result["transmitted_bits"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    received_samples_a = cast(
        list[float],
        result["received_samples_a"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    detected_bits = cast(
        list[int],
        result["detected_bits"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    zero_level_a = cast(
        float,
        result["zero_level_a"],
    )

    one_level_a = cast(
        float,
        result["one_level_a"],
    )

    threshold_a = cast(
        float,
        result["threshold_a"],
    )

    bit_indices = list(
        range(EXAMPLE_NUMBER_OF_BITS)
    )

    expected_levels_microamp = [
        (
            one_level_a
            if bit == 1
            else zero_level_a
        )
        * 1.0e6
        for bit in transmitted_bits
    ]

    received_samples_microamp = [
        sample_a * 1.0e6
        for sample_a in received_samples_a
    ]

    error_indices = [
        index
        for index, (
            transmitted_bit,
            detected_bit,
        ) in enumerate(
            zip(
                transmitted_bits,
                detected_bits,
                strict=True,
            )
        )
        if transmitted_bit != detected_bit
    ]

    error_samples_microamp = [
        received_samples_microamp[index]
        for index in error_indices
    ]

    figure, axis = plt.subplots(
        figsize=(11.0, 6.0),
    )

    axis.step(
        bit_indices,
        expected_levels_microamp,
        where="mid",
        linewidth=1.5,
        label="Expected OOK current level",
    )

    axis.plot(
        bit_indices,
        received_samples_microamp,
        linestyle="none",
        marker="o",
        markersize=4,
        label="Noisy decision sample",
    )

    axis.axhline(
        threshold_a * 1.0e6,
        linestyle="--",
        linewidth=1.5,
        label="Decision threshold",
    )

    if error_indices:
        axis.plot(
            error_indices,
            error_samples_microamp,
            linestyle="none",
            marker="x",
            markersize=9,
            label="Detection error",
        )

    axis.set_xlabel(
        "Bit index"
    )

    axis.set_ylabel(
        "Detector current (µA)"
    )

    axis.set_title(
        f"OOK decision samples at {EXAMPLE_DISTANCE_M} m"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        DETECTION_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    simulation_rows: list[
        dict[str, float | int]
    ],
) -> None:
    """Print the measured and theoretical BER results."""

    print()
    print("OOK BER distance simulation")
    print("---------------------------")

    print(
        f"Wavelength: {WAVELENGTH_NM:.0f} nm"
    )

    print(
        f"Bits per simulated distance: "
        f"{NUMBER_OF_BITS:,}"
    )

    print(
        "Detection method: midpoint threshold"
    )

    print()
    print(
        "Distance | SNR (dB) | Errors | "
        "Measured BER | Theoretical BER"
    )

    for row in simulation_rows:
        print(
            f"{float(row['distance_m']):8.0f} | "
            f"{float(row['snr_db']):8.2f} | "
            f"{int(row['error_count']):6d} | "
            f"{float(row['measured_ber']):12.6e} | "
            f"{float(row['theoretical_ber']):15.6e}"
        )

    print()
    print(
        "The simulation uses one decision sample per bit. "
        "Waveform sampling and filtering are not included yet."
    )

    print()
    print(
        f"Saved theoretical results: "
        f"{THEORY_OUTPUT_PATH}"
    )

    print(
        f"Saved simulated results: "
        f"{SIMULATION_OUTPUT_PATH}"
    )

    print(
        f"Saved BER figure: "
        f"{BER_FIGURE_PATH}"
    )

    print(
        f"Saved detection figure: "
        f"{DETECTION_FIGURE_PATH}"
    )


def main() -> None:
    """Run the OOK BER distance study."""

    theory_rows = calculate_theoretical_sweep()

    simulation_rows, example_result = (
        run_simulated_points()
    )

    write_theoretical_results(
        rows=theory_rows,
    )

    write_simulation_results(
        rows=simulation_rows,
    )

    create_ber_figure(
        theory_rows=theory_rows,
        simulation_rows=simulation_rows,
    )

    create_detection_figure(
        result=example_result,
    )

    print_summary(
        simulation_rows=simulation_rows,
    )


if __name__ == "__main__":
    main()