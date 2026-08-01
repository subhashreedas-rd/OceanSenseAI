"""Evaluate receiver-bandwidth limitation and OOK intersymbol interference.

This study isolates deterministic pulse distortion from receiver noise.

The detector and electronics decision-noise variance remains fixed at the
baseline value established earlier. Only the first-order receiver cutoff
frequency is varied. This shows how limited bandwidth closes the eye and
changes BER without mixing that effect with a changing noise bandwidth.
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
from src.ook import generate_bits  # noqa: E402
from src.receiver_filter import simulate_bandlimited_ook  # noqa: E402


RESULTS_DIR = ROOT_DIR / "studies" / "study_02" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_02"

OUTPUT_CSV_PATH = (
    RESULTS_DIR
    / "receiver_bandwidth_isi_comparison.csv"
)

BER_FIGURE_PATH = (
    FIGURES_DIR
    / "receiver_bandwidth_ber_comparison.png"
)

EYE_FIGURE_PATH = (
    FIGURES_DIR
    / "receiver_bandwidth_eye_opening.png"
)

WAVEFORM_FIGURE_PATH = (
    FIGURES_DIR
    / "receiver_bandwidth_waveform_comparison.png"
)


# Study 01 channel condition.
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
NOISE_BANDWIDTH_HZ = 100.0e6
TEMPERATURE_K = 300.0
LOAD_RESISTANCE_OHM = 1000.0

# Signal-processing configuration.
DISTANCE_M = 442.0
BIT_RATE_HZ = 20.0e6
SAMPLES_PER_BIT = 16
SAMPLING_FRACTION = 1.0

RECEIVER_CUTOFF_VALUES_HZ = (
    40.0e6,
    20.0e6,
    10.0e6,
    5.0e6,
    2.0e6,
    1.0e6,
)

NUMBER_OF_BITS = 30_000
BIT_SEQUENCE_SEED = 20260801
NOISE_SEED_BASE = 15_000

EXAMPLE_NUMBER_OF_BITS = 24
HIGH_BANDWIDTH_EXAMPLE_HZ = 40.0e6
LOW_BANDWIDTH_EXAMPLE_HZ = 2.0e6

BER_FIGURE_FLOOR = 1.0e-5


def calculate_receiver_state() -> dict[str, float]:
    """Calculate the physical receiver state at the selected distance."""

    return calculate_link_budget(
        transmitted_power_w=TRANSMITTED_POWER_W,
        attenuation_per_m=ATTENUATION_PER_M,
        distance_m=DISTANCE_M,
        initial_beam_radius_m=INITIAL_BEAM_RADIUS_M,
        divergence_half_angle_rad=(
            DIVERGENCE_HALF_ANGLE_RAD
        ),
        receiver_radius_m=RECEIVER_RADIUS_M,
        system_efficiency=SYSTEM_EFFICIENCY,
        responsivity_a_per_w=RESPONSIVITY_A_PER_W,
        background_power_w=BACKGROUND_POWER_W,
        dark_current_a=DARK_CURRENT_A,
        bandwidth_hz=NOISE_BANDWIDTH_HZ,
        temperature_k=TEMPERATURE_K,
        load_resistance_ohm=LOAD_RESISTANCE_OHM,
    )


def run_bandwidth_comparison() -> tuple[
    list[dict[str, float | int]],
    dict[
        float,
        dict[
            str,
            float | int | list[int] | list[float],
        ],
    ],
    dict[str, float],
]:
    """Run the receiver simulation for all cutoff frequencies."""

    link = calculate_receiver_state()

    transmitted_bits = generate_bits(
        number_of_bits=NUMBER_OF_BITS,
        seed=BIT_SEQUENCE_SEED,
    )

    rows: list[dict[str, float | int]] = []

    stored_results: dict[
        float,
        dict[
            str,
            float | int | list[int] | list[float],
        ],
    ] = {}

    for index, cutoff_hz in enumerate(
        RECEIVER_CUTOFF_VALUES_HZ
    ):
        result = simulate_bandlimited_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=link["signal_current_a"],
            background_current_a=link[
                "background_current_a"
            ],
            dark_current_a=DARK_CURRENT_A,
            bandwidth_hz=NOISE_BANDWIDTH_HZ,
            temperature_k=TEMPERATURE_K,
            load_resistance_ohm=LOAD_RESISTANCE_OHM,
            bit_rate_hz=BIT_RATE_HZ,
            receiver_cutoff_hz=cutoff_hz,
            samples_per_bit=SAMPLES_PER_BIT,
            sampling_fraction=SAMPLING_FRACTION,
            seed=NOISE_SEED_BASE + index,
        )

        measured_ber = cast(
            float,
            result["ber"],
        )

        ideal_ber = cast(
            float,
            result["ideal_no_isi_ber"],
        )

        rows.append(
            {
                "receiver_cutoff_hz": cutoff_hz,
                "cutoff_to_bit_rate_ratio": (
                    cutoff_hz / BIT_RATE_HZ
                ),
                "error_count": cast(
                    int,
                    result["error_count"],
                ),
                "measured_ber": measured_ber,
                "ideal_no_isi_ber": ideal_ber,
                "ber_increase": (
                    measured_ber - ideal_ber
                ),
                "normalized_eye_opening": cast(
                    float,
                    result["normalized_eye_opening"],
                ),
                "eye_opening_a": cast(
                    float,
                    result["eye_opening_a"],
                ),
                "mean_level_separation_a": cast(
                    float,
                    result["mean_level_separation_a"],
                ),
                "snr_db": link["snr_db"],
            }
        )

        if cutoff_hz in (
            HIGH_BANDWIDTH_EXAMPLE_HZ,
            LOW_BANDWIDTH_EXAMPLE_HZ,
        ):
            stored_results[cutoff_hz] = result

    required_examples = {
        HIGH_BANDWIDTH_EXAMPLE_HZ,
        LOW_BANDWIDTH_EXAMPLE_HZ,
    }

    if set(stored_results) != required_examples:
        raise RuntimeError(
            "Required waveform examples were not simulated"
        )

    return rows, stored_results, link


def write_results(
    rows: list[dict[str, float | int]],
) -> None:
    """Write the bandwidth comparison to CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "receiver_cutoff_hz",
        "cutoff_to_bit_rate_ratio",
        "error_count",
        "measured_ber",
        "ideal_no_isi_ber",
        "ber_increase",
        "normalized_eye_opening",
        "eye_opening_a",
        "mean_level_separation_a",
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
            writer.writerow(
                {
                    "receiver_cutoff_hz": (
                        f"{float(row['receiver_cutoff_hz']):.12e}"
                    ),
                    "cutoff_to_bit_rate_ratio": (
                        f"{float(row['cutoff_to_bit_rate_ratio']):.12e}"
                    ),
                    "error_count": int(
                        row["error_count"]
                    ),
                    "measured_ber": (
                        f"{float(row['measured_ber']):.12e}"
                    ),
                    "ideal_no_isi_ber": (
                        f"{float(row['ideal_no_isi_ber']):.12e}"
                    ),
                    "ber_increase": (
                        f"{float(row['ber_increase']):.12e}"
                    ),
                    "normalized_eye_opening": (
                        f"{float(row['normalized_eye_opening']):.12e}"
                    ),
                    "eye_opening_a": (
                        f"{float(row['eye_opening_a']):.12e}"
                    ),
                    "mean_level_separation_a": (
                        f"{float(row['mean_level_separation_a']):.12e}"
                    ),
                    "snr_db": (
                        f"{float(row['snr_db']):.12e}"
                    ),
                }
            )


def create_ber_figure(
    rows: list[dict[str, float | int]],
) -> None:
    """Plot BER against normalized receiver bandwidth."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    sorted_rows = sorted(
        rows,
        key=lambda row: float(
            row["cutoff_to_bit_rate_ratio"]
        ),
    )

    ratios = [
        float(row["cutoff_to_bit_rate_ratio"])
        for row in sorted_rows
    ]

    measured_ber = [
        max(
            float(row["measured_ber"]),
            BER_FIGURE_FLOOR,
        )
        for row in sorted_rows
    ]

    ideal_ber = float(
        sorted_rows[0]["ideal_no_isi_ber"]
    )

    figure, axis = plt.subplots(
        figsize=(8.5, 5.5),
    )

    axis.semilogy(
        ratios,
        measured_ber,
        marker="o",
        markersize=7,
        linewidth=1.5,
        label="Bandwidth-limited measured BER",
    )

    axis.axhline(
        ideal_ber,
        linestyle="--",
        linewidth=1.5,
        label="Ideal no-ISI BER",
    )

    axis.set_xlabel(
        "Receiver cutoff / bit rate"
    )

    axis.set_ylabel(
        "Bit-error rate"
    )

    axis.set_title(
        "Effect of receiver bandwidth on OOK BER"
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


def create_eye_figure(
    rows: list[dict[str, float | int]],
) -> None:
    """Plot normalized eye opening against receiver bandwidth."""

    sorted_rows = sorted(
        rows,
        key=lambda row: float(
            row["cutoff_to_bit_rate_ratio"]
        ),
    )

    ratios = [
        float(row["cutoff_to_bit_rate_ratio"])
        for row in sorted_rows
    ]

    normalized_eye_opening = [
        float(row["normalized_eye_opening"])
        for row in sorted_rows
    ]

    figure, axis = plt.subplots(
        figsize=(8.5, 5.5),
    )

    axis.plot(
        ratios,
        normalized_eye_opening,
        marker="o",
        markersize=7,
        linewidth=1.5,
    )

    axis.axhline(
        0.0,
        linestyle="--",
        linewidth=1.0,
        label="Closed-eye boundary",
    )

    axis.set_xlabel(
        "Receiver cutoff / bit rate"
    )

    axis.set_ylabel(
        "Normalized noiseless eye opening"
    )

    axis.set_title(
        "Receiver-bandwidth-induced eye closure"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        EYE_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def create_waveform_figure(
    stored_results: dict[
        float,
        dict[
            str,
            float | int | list[int] | list[float],
        ],
    ],
) -> None:
    """Compare high- and low-bandwidth filtered waveforms."""

    high_result = stored_results[
        HIGH_BANDWIDTH_EXAMPLE_HZ
    ]

    low_result = stored_results[
        LOW_BANDWIDTH_EXAMPLE_HZ
    ]

    samples_to_plot = (
        EXAMPLE_NUMBER_OF_BITS
        * SAMPLES_PER_BIT
    )

    clean_waveform_a = cast(
        list[float],
        high_result["clean_waveform_a"],
    )[:samples_to_plot]

    high_filtered_a = cast(
        list[float],
        high_result["filtered_waveform_a"],
    )[:samples_to_plot]

    low_filtered_a = cast(
        list[float],
        low_result["filtered_waveform_a"],
    )[:samples_to_plot]

    sample_positions = [
        sample_index / SAMPLES_PER_BIT
        for sample_index in range(
            samples_to_plot
        )
    ]

    clean_microamp = [
        value * 1.0e6
        for value in clean_waveform_a
    ]

    high_microamp = [
        value * 1.0e6
        for value in high_filtered_a
    ]

    low_microamp = [
        value * 1.0e6
        for value in low_filtered_a
    ]

    figure, axis = plt.subplots(
        figsize=(12.0, 6.0),
    )

    axis.step(
        sample_positions,
        clean_microamp,
        where="post",
        linewidth=1.2,
        label="Ideal rectangular OOK waveform",
    )

    axis.plot(
        sample_positions,
        high_microamp,
        linewidth=1.6,
        label=(
            f"{HIGH_BANDWIDTH_EXAMPLE_HZ / 1.0e6:.0f} MHz cutoff"
        ),
    )

    axis.plot(
        sample_positions,
        low_microamp,
        linewidth=1.8,
        label=(
            f"{LOW_BANDWIDTH_EXAMPLE_HZ / 1.0e6:.0f} MHz cutoff"
        ),
    )

    axis.set_xlabel(
        "Bit interval"
    )

    axis.set_ylabel(
        "Detector current (µA)"
    )

    axis.set_title(
        "Bandwidth-limited OOK pulse distortion"
    )

    axis.grid(
        True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        WAVEFORM_FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    rows: list[dict[str, float | int]],
    link: dict[str, float],
) -> None:
    """Print the receiver-bandwidth comparison."""

    print()
    print("Receiver bandwidth and ISI comparison")
    print("-------------------------------------")

    print(
        f"Distance: {DISTANCE_M:.0f} m"
    )

    print(
        f"Bit rate: {BIT_RATE_HZ / 1.0e6:.1f} Mbit/s"
    )

    print(
        f"Receiver SNR: {link['snr_db']:.2f} dB"
    )

    print(
        f"Bits per case: {NUMBER_OF_BITS:,}"
    )

    print()
    print(
        "Cutoff | fc/Rb | Eye opening | Errors | "
        "Measured BER | Ideal BER"
    )

    for row in rows:
        print(
            f"{float(row['receiver_cutoff_hz']) / 1.0e6:6.1f} MHz | "
            f"{float(row['cutoff_to_bit_rate_ratio']):5.2f} | "
            f"{float(row['normalized_eye_opening']):11.4f} | "
            f"{int(row['error_count']):6d} | "
            f"{float(row['measured_ber']):12.6e} | "
            f"{float(row['ideal_no_isi_ber']):9.6e}"
        )

    print()
    print(
        "Noise bandwidth remains fixed in this study. "
        "The comparison isolates pulse distortion and ISI."
    )

    print()
    print(f"Saved results: {OUTPUT_CSV_PATH}")
    print(f"Saved BER figure: {BER_FIGURE_PATH}")
    print(f"Saved eye figure: {EYE_FIGURE_PATH}")
    print(
        f"Saved waveform figure: "
        f"{WAVEFORM_FIGURE_PATH}"
    )


def main() -> None:
    """Run the receiver-bandwidth study."""

    rows, stored_results, link = (
        run_bandwidth_comparison()
    )

    write_results(
        rows=rows,
    )

    create_ber_figure(
        rows=rows,
    )

    create_eye_figure(
        rows=rows,
    )

    create_waveform_figure(
        stored_results=stored_results,
    )

    print_summary(
        rows=rows,
        link=link,
    )


if __name__ == "__main__":
    main()