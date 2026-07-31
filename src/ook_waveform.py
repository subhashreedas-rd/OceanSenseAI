"""Sampled current-domain OOK waveform generation and detection.

The processing chain is:

    binary bits
    -> rectangular OOK waveform
    -> state-dependent Gaussian receiver noise
    -> rectangular matched filter
    -> one decision sample per bit
    -> threshold detection
    -> recovered bits and BER

The sample-noise variance is scaled so that averaging one complete bit
interval produces the same decision-noise variance as the verified
bit-level receiver model. Increasing the samples per bit therefore does
not create an artificial SNR improvement.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from src.ook import (
    bit_error_count,
    detect_ook_samples,
    midpoint_threshold,
    ook_current_levels,
    ook_noise_variances,
    theoretical_midpoint_ber,
    validate_bits,
)


def _require_finite(
    value: float,
    name: str,
) -> None:
    """Require a finite numerical value."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_non_negative(
    value: float,
    name: str,
) -> None:
    """Require a finite value greater than or equal to zero."""

    _require_finite(value, name)

    if value < 0.0:
        raise ValueError(
            f"{name} must be non-negative"
        )


def _require_positive_integer(
    value: int,
    name: str,
) -> None:
    """Require a positive integer."""

    if not isinstance(value, int):
        raise TypeError(
            f"{name} must be an integer"
        )

    if value <= 0:
        raise ValueError(
            f"{name} must be positive"
        )


def _validate_current_levels(
    zero_level_a: float,
    one_level_a: float,
) -> None:
    """Validate the two OOK current levels."""

    _require_non_negative(
        zero_level_a,
        "zero_level_a",
    )

    _require_non_negative(
        one_level_a,
        "one_level_a",
    )

    if one_level_a < zero_level_a:
        raise ValueError(
            "one_level_a must not be below zero_level_a"
        )


def generate_rectangular_ook_waveform(
    bits: Sequence[int],
    zero_level_a: float,
    one_level_a: float,
    samples_per_bit: int,
) -> list[float]:
    """Generate a rectangular sampled OOK current waveform."""

    validate_bits(bits)

    _validate_current_levels(
        zero_level_a=zero_level_a,
        one_level_a=one_level_a,
    )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    waveform_a: list[float] = []

    for bit in bits:
        level_a = (
            one_level_a
            if bit == 1
            else zero_level_a
        )

        waveform_a.extend(
            [level_a] * samples_per_bit
        )

    return waveform_a


def sample_noise_variance(
    decision_noise_variance_a2: float,
    samples_per_bit: int,
) -> float:
    """Convert decision variance into per-sample variance.

    For N independent samples with variance N times the desired decision
    variance, averaging the N samples produces the desired variance:

        var(mean) = (N * decision_variance) / N
                  = decision_variance
    """

    _require_non_negative(
        decision_noise_variance_a2,
        "decision_noise_variance_a2",
    )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    return (
        decision_noise_variance_a2
        * samples_per_bit
    )


def add_state_dependent_waveform_noise(
    bits: Sequence[int],
    clean_waveform_a: Sequence[float],
    zero_decision_variance_a2: float,
    one_decision_variance_a2: float,
    samples_per_bit: int,
    seed: int | None = None,
) -> list[float]:
    """Add independent Gaussian noise to each waveform sample.

    The zero and one states use separate noise variances because the one
    state contains additional signal-dependent shot noise.
    """

    validate_bits(bits)

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    expected_sample_count = (
        len(bits)
        * samples_per_bit
    )

    if len(clean_waveform_a) != expected_sample_count:
        raise ValueError(
            "clean_waveform_a length must equal "
            "len(bits) * samples_per_bit"
        )

    zero_sample_variance_a2 = sample_noise_variance(
        decision_noise_variance_a2=(
            zero_decision_variance_a2
        ),
        samples_per_bit=samples_per_bit,
    )

    one_sample_variance_a2 = sample_noise_variance(
        decision_noise_variance_a2=(
            one_decision_variance_a2
        ),
        samples_per_bit=samples_per_bit,
    )

    zero_sample_standard_deviation_a = math.sqrt(
        zero_sample_variance_a2
    )

    one_sample_standard_deviation_a = math.sqrt(
        one_sample_variance_a2
    )

    random_generator = random.Random(seed)

    noisy_waveform_a: list[float] = []

    for bit_index, bit in enumerate(bits):
        block_start = (
            bit_index
            * samples_per_bit
        )

        block_end = (
            block_start
            + samples_per_bit
        )

        standard_deviation_a = (
            one_sample_standard_deviation_a
            if bit == 1
            else zero_sample_standard_deviation_a
        )

        for clean_sample_a in clean_waveform_a[
            block_start:block_end
        ]:
            _require_finite(
                clean_sample_a,
                "clean_waveform_a sample",
            )

            noisy_waveform_a.append(
                random_generator.gauss(
                    clean_sample_a,
                    standard_deviation_a,
                )
            )

    return noisy_waveform_a


def rectangular_matched_filter(
    received_waveform_a: Sequence[float],
    samples_per_bit: int,
) -> list[float]:
    """Apply a moving rectangular averaging filter.

    At the final sample of each bit interval, the output equals the
    integrate-and-dump decision value for that bit.
    """

    if len(received_waveform_a) == 0:
        raise ValueError(
            "received_waveform_a must not be empty"
        )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    filtered_waveform_a: list[float] = []

    running_sum_a = 0.0

    for index, sample_a in enumerate(
        received_waveform_a
    ):
        _require_finite(
            sample_a,
            f"received_waveform_a[{index}]",
        )

        running_sum_a += sample_a

        if index >= samples_per_bit:
            running_sum_a -= (
                received_waveform_a[
                    index - samples_per_bit
                ]
            )

        available_samples = min(
            index + 1,
            samples_per_bit,
        )

        filtered_waveform_a.append(
            running_sum_a
            / available_samples
        )

    return filtered_waveform_a


def decision_sample_indices(
    number_of_bits: int,
    samples_per_bit: int,
) -> list[int]:
    """Return the end-of-bit matched-filter sample indices."""

    _require_positive_integer(
        number_of_bits,
        "number_of_bits",
    )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    return [
        (
            (bit_index + 1)
            * samples_per_bit
            - 1
        )
        for bit_index in range(number_of_bits)
    ]


def extract_matched_filter_decisions(
    filtered_waveform_a: Sequence[float],
    number_of_bits: int,
    samples_per_bit: int,
) -> list[float]:
    """Extract one matched-filter decision sample per bit."""

    indices = decision_sample_indices(
        number_of_bits=number_of_bits,
        samples_per_bit=samples_per_bit,
    )

    required_length = (
        number_of_bits
        * samples_per_bit
    )

    if len(filtered_waveform_a) != required_length:
        raise ValueError(
            "filtered_waveform_a length must equal "
            "number_of_bits * samples_per_bit"
        )

    return [
        filtered_waveform_a[index]
        for index in indices
    ]


def integrate_and_dump(
    received_waveform_a: Sequence[float],
    samples_per_bit: int,
) -> list[float]:
    """Average each non-overlapping bit interval."""

    if len(received_waveform_a) == 0:
        raise ValueError(
            "received_waveform_a must not be empty"
        )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    if (
        len(received_waveform_a)
        % samples_per_bit
        != 0
    ):
        raise ValueError(
            "Waveform length must be divisible by "
            "samples_per_bit"
        )

    decision_samples_a: list[float] = []

    for block_start in range(
        0,
        len(received_waveform_a),
        samples_per_bit,
    ):
        block = received_waveform_a[
            block_start:
            block_start + samples_per_bit
        ]

        for sample_a in block:
            _require_finite(
                sample_a,
                "received_waveform_a sample",
            )

        decision_samples_a.append(
            sum(block)
            / samples_per_bit
        )

    return decision_samples_a


def simulate_sampled_ook(
    transmitted_bits: Sequence[int],
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
    samples_per_bit: int,
    seed: int | None = None,
) -> dict[
    str,
    float | int | list[int] | list[float],
]:
    """Run the complete sampled OOK waveform simulation."""

    validate_bits(transmitted_bits)

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    zero_level_a, one_level_a = ook_current_levels(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
    )

    zero_decision_variance_a2, (
        one_decision_variance_a2
    ) = ook_noise_variances(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
        temperature_k=temperature_k,
        load_resistance_ohm=load_resistance_ohm,
    )

    clean_waveform_a = (
        generate_rectangular_ook_waveform(
            bits=transmitted_bits,
            zero_level_a=zero_level_a,
            one_level_a=one_level_a,
            samples_per_bit=samples_per_bit,
        )
    )

    noisy_waveform_a = (
        add_state_dependent_waveform_noise(
            bits=transmitted_bits,
            clean_waveform_a=clean_waveform_a,
            zero_decision_variance_a2=(
                zero_decision_variance_a2
            ),
            one_decision_variance_a2=(
                one_decision_variance_a2
            ),
            samples_per_bit=samples_per_bit,
            seed=seed,
        )
    )

    filtered_waveform_a = rectangular_matched_filter(
        received_waveform_a=noisy_waveform_a,
        samples_per_bit=samples_per_bit,
    )

    decision_samples_a = (
        extract_matched_filter_decisions(
            filtered_waveform_a=(
                filtered_waveform_a
            ),
            number_of_bits=len(
                transmitted_bits
            ),
            samples_per_bit=samples_per_bit,
        )
    )

    direct_decision_samples_a = integrate_and_dump(
        received_waveform_a=noisy_waveform_a,
        samples_per_bit=samples_per_bit,
    )

    for filtered_value, direct_value in zip(
        decision_samples_a,
        direct_decision_samples_a,
        strict=True,
    ):
        if not math.isclose(
            filtered_value,
            direct_value,
            rel_tol=1.0e-12,
            abs_tol=1.0e-18,
        ):
            raise RuntimeError(
                "Matched-filter and integrate-and-dump "
                "decision values disagree"
            )

    threshold_a = midpoint_threshold(
        zero_level_a=zero_level_a,
        one_level_a=one_level_a,
    )

    detected_bits = detect_ook_samples(
        received_samples_a=decision_samples_a,
        threshold_a=threshold_a,
    )

    error_count = bit_error_count(
        transmitted_bits=transmitted_bits,
        detected_bits=detected_bits,
    )

    measured_ber = (
        error_count
        / len(transmitted_bits)
    )

    predicted_ber = theoretical_midpoint_ber(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
        temperature_k=temperature_k,
        load_resistance_ohm=load_resistance_ohm,
    )

    return {
        "transmitted_bits": list(
            transmitted_bits
        ),
        "clean_waveform_a": clean_waveform_a,
        "noisy_waveform_a": noisy_waveform_a,
        "filtered_waveform_a": (
            filtered_waveform_a
        ),
        "decision_samples_a": (
            decision_samples_a
        ),
        "detected_bits": detected_bits,
        "samples_per_bit": samples_per_bit,
        "zero_level_a": zero_level_a,
        "one_level_a": one_level_a,
        "threshold_a": threshold_a,
        "zero_decision_variance_a2": (
            zero_decision_variance_a2
        ),
        "one_decision_variance_a2": (
            one_decision_variance_a2
        ),
        "zero_sample_variance_a2": (
            sample_noise_variance(
                zero_decision_variance_a2,
                samples_per_bit,
            )
        ),
        "one_sample_variance_a2": (
            sample_noise_variance(
                one_decision_variance_a2,
                samples_per_bit,
            )
        ),
        "error_count": error_count,
        "ber": measured_ber,
        "theoretical_ber": predicted_ber,
    }