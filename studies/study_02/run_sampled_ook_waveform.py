"""Compare sampled OOK waveform detection across oversampling factors.

The processing chain is:

    generated bits
    -> rectangular OOK current waveform
    -> state-dependent receiver noise
    -> rectangular matched filter
    -> decision sampling
    -> threshold detection
    -> recovered bits and BER

The per-sample noise variance is scaled so that each bit decision retains
the noise variance established by the verified receiver model. Increasing
the number of samples per bit therefore improves waveform representation
without creating artificial detector performance.
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
from src.ook_waveform import simulate_sampled_ook  # noqa: E402


RESULTS_DIR = ROOT_DIR / "studies" / "study_02" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_02"

OUTPUT_CSV_PATH = (
    RESULTS_DIR
    / "sampled_ook_oversampling_comparison.csv"
)

BER_FIGURE_PATH = (
    FIGURES_DIR
    / "sampled_ook_oversampling_ber_comparison.png"
)

WAVEFORM_FIGURE_PATH = (
    FIGURES_DIR
    / "sampled_ook_waveform_example_442m.png"
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
BANDWIDTH_HZ = 100.0e6
TEMPERATURE_K = 300.0
LOAD_RESISTANCE_OHM = 1000.0

# Signal-processing configuration.
DISTANCE_M = 442.0

SAMPLES_PER_BIT_VALUES = (
    1,
    4,
    8,
    16,
)

NUMBER_OF_BITS = 50_000
BIT_SEQUENCE_SEED = 20260731
NOISE_SEED_BASE = 12_000

EXAMPLE_SAMPLES_PER_BIT = 8
EXAMPLE_NUMBER_OF_BITS = 30

BER_FIGURE_FLOOR = 1.0e-6


def calculate_receiver_state() -> dict[str, float]:
    """Calculate the physical receiver state at the study distance."""

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
        bandwidth_hz=BANDWIDTH_HZ,
        temperature_k=TEMPERATURE_K,
        load_resistance_ohm=LOAD_RESISTANCE_OHM,
    )


def run_oversampling_comparison() -> tuple[
    list[dict[str, float | int]],
    dict[str, float | int | list[int] | list[float]],
    dict[str, float],
]:
    """Run waveform simulations at several samples-per-bit values."""

    link = calculate_receiver_state()

    transmitted_bits = generate_bits(
        number_of_bits=NUMBER_OF_BITS,
        seed=BIT_SEQUENCE_SEED,
    )

    rows: list[dict[str, float | int]] = []

    example_result: (
        dict[
            str,
            float | int | list[int] | list[float],
        ]
        | None
    ) = None

    for index, samples_per_bit in enumerate(
        SAMPLES_PER_BIT_VALUES
    ):
        result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=link["signal_current_a"],
            background_current_a=link[
                "background_current_a"
            ],
            dark_current_a=DARK_CURRENT_A,
            bandwidth_hz=BANDWIDTH_HZ,
            temperature_k=TEMPERATURE_K,
            load_resistance_ohm=LOAD_RESISTANCE_OHM,
            samples_per_bit=samples_per_bit,
            seed=NOISE_SEED_BASE + index,
        )

        measured_ber = cast(
            float,
            result["ber"],
        )

        theoretical_ber = cast(
            float,
            result["theoretical_ber"],
        )

        rows.append(
            {
                "samples_per_bit": samples_per_bit,
                "total_waveform_samples": (
                    NUMBER_OF_BITS
                    * samples_per_bit
                ),
                "error_count": cast(
                    int,
                    result["error_count"],
                ),
                "measured_ber": measured_ber,
                "theoretical_ber": theoretical_ber,
                "absolute_ber_difference": abs(
                    measured_ber
                    - theoretical_ber
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

        if samples_per_bit == EXAMPLE_SAMPLES_PER_BIT:
            example_result = result

    if example_result is None:
        raise RuntimeError(
            "The requested example samples-per-bit "
            "value was not simulated"
        )

    return rows, example_result, link


def write_results(
    rows: list[dict[str, float | int]],
) -> None:
    """Write the oversampling comparison to CSV."""

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "samples_per_bit",
        "total_waveform_samples",
        "error_count",
        "measured_ber",
        "theoretical_ber",
        "absolute_ber_difference",
        "snr_db",
        "received_power_w",
        "signal_current_a",
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
                    "samples_per_bit": int(
                        row["samples_per_bit"]
                    ),
                    "total_waveform_samples": int(
                        row["total_waveform_samples"]
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
                    "absolute_ber_difference": (
                        f"{float(row['absolute_ber_difference']):.12e}"
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


def create_ber_comparison_figure(
    rows: list[dict[str, float | int]],
) -> None:
    """Plot measured BER against samples per bit."""

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    samples_per_bit = [
        int(row["samples_per_bit"])
        for row in rows
    ]

    measured_ber = [
        max(
            float(row["measured_ber"]),
            BER_FIGURE_FLOOR,
        )
        for row in rows
    ]

    theoretical_ber = float(
        rows[0]["theoretical_ber"]
    )

    figure, axis = plt.subplots(
        figsize=(8.5, 5.5),
    )

    axis.semilogy(
        samples_per_bit,
        measured_ber,
        marker="o",
        markersize=7,
        linewidth=1.5,
        label="Measured sampled-waveform BER",
    )

    axis.axhline(
        theoretical_ber,
        linestyle="--",
        linewidth=1.5,
        label="Bit-level theoretical BER",
    )

    axis.set_xlabel(
        "Samples per bit"
    )

    axis.set_ylabel(
        "Bit-error rate"
    )

    axis.set_title(
        f"Sampled OOK BER comparison at {DISTANCE_M:.0f} m"
    )

    axis.set_xticks(
        list(SAMPLES_PER_BIT_VALUES)
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


def create_waveform_figure(
    result: dict[
        str,
        float | int | list[int] | list[float],
    ],
) -> None:
    """Plot clean, noisy, and matched-filtered waveforms."""

    samples_per_bit = cast(
        int,
        result["samples_per_bit"],
    )

    sample_count = (
        EXAMPLE_NUMBER_OF_BITS
        * samples_per_bit
    )

    transmitted_bits = cast(
        list[int],
        result["transmitted_bits"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    detected_bits = cast(
        list[int],
        result["detected_bits"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    clean_waveform_a = cast(
        list[float],
        result["clean_waveform_a"],
    )[:sample_count]

    noisy_waveform_a = cast(
        list[float],
        result["noisy_waveform_a"],
    )[:sample_count]

    filtered_waveform_a = cast(
        list[float],
        result["filtered_waveform_a"],
    )[:sample_count]

    decision_samples_a = cast(
        list[float],
        result["decision_samples_a"],
    )[:EXAMPLE_NUMBER_OF_BITS]

    threshold_a = cast(
        float,
        result["threshold_a"],
    )

    sample_positions = [
        sample_index / samples_per_bit
        for sample_index in range(sample_count)
    ]

    decision_positions = [
        (
            (bit_index + 1)
            * samples_per_bit
            - 1
        )
        / samples_per_bit
        for bit_index in range(
            EXAMPLE_NUMBER_OF_BITS
        )
    ]

    clean_microamp = [
        value * 1.0e6
        for value in clean_waveform_a
    ]

    noisy_microamp = [
        value * 1.0e6
        for value in noisy_waveform_a
    ]

    filtered_microamp = [
        value * 1.0e6
        for value in filtered_waveform_a
    ]

    decisions_microamp = [
        value * 1.0e6
        for value in decision_samples_a
    ]

    error_positions = [
        decision_positions[index]
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

    error_values_microamp = [
        decisions_microamp[index]
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

    figure, axis = plt.subplots(
        figsize=(12.0, 6.5),
    )

    axis.step(
        sample_positions,
        clean_microamp,
        where="post",
        linewidth=1.5,
        label="Clean OOK waveform",
    )

    axis.plot(
        sample_positions,
        noisy_microamp,
        linewidth=0.8,
        alpha=0.7,
        label="Noisy received waveform",
    )

    axis.plot(
        sample_positions,
        filtered_microamp,
        linewidth=1.8,
        label="Rectangular matched-filter output",
    )

    axis.plot(
        decision_positions,
        decisions_microamp,
        linestyle="none",
        marker="o",
        markersize=5,
        label="Decision samples",
    )

    axis.axhline(
        threshold_a * 1.0e6,
        linestyle="--",
        linewidth=1.5,
        label="Decision threshold",
    )

    if error_positions:
        axis.plot(
            error_positions,
            error_values_microamp,
            linestyle="none",
            marker="x",
            markersize=10,
            label="Detection error",
        )

    axis.set_xlabel(
        "Bit interval"
    )

    axis.set_ylabel(
        "Detector current (µA)"
    )

    axis.set_title(
        f"Sampled OOK processing at {DISTANCE_M:.0f} m "
        f"({samples_per_bit} samples per bit)"
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
    """Print the sampled-waveform verification results."""

    print()
    print("Sampled OOK waveform comparison")
    print("-------------------------------")

    print(
        f"Distance: {DISTANCE_M:.0f} m"
    )

    print(
        f"Wavelength: {WAVELENGTH_NM:.0f} nm"
    )

    print(
        f"Receiver SNR: {link['snr_db']:.2f} dB"
    )

    print(
        f"Bits per simulation: {NUMBER_OF_BITS:,}"
    )

    print()
    print(
        "Samples/bit | Samples | Errors | "
        "Measured BER | Theoretical BER"
    )

    for row in rows:
        print(
            f"{int(row['samples_per_bit']):11d} | "
            f"{int(row['total_waveform_samples']):7d} | "
            f"{int(row['error_count']):6d} | "
            f"{float(row['measured_ber']):12.6e} | "
            f"{float(row['theoretical_ber']):15.6e}"
        )

    maximum_difference = max(
        float(row["absolute_ber_difference"])
        for row in rows
    )

    print()
    print(
        "Maximum absolute measured-to-theoretical "
        f"BER difference: {maximum_difference:.6e}"
    )

    print()
    print(
        "Oversampling changes waveform resolution, "
        "not the established decision SNR."
    )

    print()
    print(f"Saved results: {OUTPUT_CSV_PATH}")
    print(f"Saved BER figure: {BER_FIGURE_PATH}")
    print(
        f"Saved waveform figure: "
        f"{WAVEFORM_FIGURE_PATH}"
    )


def main() -> None:
    """Run the sampled OOK waveform study."""

    rows, example_result, link = (
        run_oversampling_comparison()
    )

    write_results(
        rows=rows,
    )

    create_ber_comparison_figure(
        rows=rows,
    )

    create_waveform_figure(
        result=example_result,
    )

    print_summary(
        rows=rows,
        link=link,
    )


if __name__ == "__main__":
    main()