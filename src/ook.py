"""Current-domain on-off keying generation and detection.

The model represents the photodetector output using two current levels:

    bit 0: background current + dark current
    bit 1: signal current + background current + dark current

Independent Gaussian noise is added using the shot-noise and thermal-noise
variances calculated by the receiver model.

This is a bit-level baseline model with one decision sample per bit.
Pulse shaping, sampling rate, filtering, timing recovery, and waveform
processing are intentionally handled in later modules.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from src.link_budget import (
    shot_noise_variance,
    thermal_noise_variance,
    total_noise_variance,
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
        raise ValueError(f"{name} must be non-negative")


def _require_positive(
    value: float,
    name: str,
) -> None:
    """Require a finite value greater than zero."""

    _require_finite(value, name)

    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def validate_bits(
    bits: Sequence[int],
) -> None:
    """Validate a non-empty binary sequence."""

    if len(bits) == 0:
        raise ValueError("bits must not be empty")

    for index, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError(
                f"bits[{index}] must be 0 or 1"
            )


def generate_bits(
    number_of_bits: int,
    seed: int | None = None,
) -> list[int]:
    """Generate a reproducible random binary sequence."""

    if not isinstance(number_of_bits, int):
        raise TypeError(
            "number_of_bits must be an integer"
        )

    if number_of_bits <= 0:
        raise ValueError(
            "number_of_bits must be positive"
        )

    random_generator = random.Random(seed)

    return [
        random_generator.getrandbits(1)
        for _ in range(number_of_bits)
    ]


def ook_current_levels(
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
) -> tuple[float, float]:
    """Return the expected detector-current levels for bits 0 and 1."""

    _require_non_negative(
        signal_current_a,
        "signal_current_a",
    )

    _require_non_negative(
        background_current_a,
        "background_current_a",
    )

    _require_non_negative(
        dark_current_a,
        "dark_current_a",
    )

    zero_level_a = (
        background_current_a
        + dark_current_a
    )

    one_level_a = (
        zero_level_a
        + signal_current_a
    )

    return zero_level_a, one_level_a


def ook_noise_variances(
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
) -> tuple[float, float]:
    """Calculate noise variance for the zero and one states.

    The one state has additional shot noise because it contains the
    received signal photocurrent.
    """

    _require_non_negative(
        signal_current_a,
        "signal_current_a",
    )

    _require_non_negative(
        background_current_a,
        "background_current_a",
    )

    _require_non_negative(
        dark_current_a,
        "dark_current_a",
    )

    _require_positive(
        bandwidth_hz,
        "bandwidth_hz",
    )

    _require_positive(
        temperature_k,
        "temperature_k",
    )

    _require_positive(
        load_resistance_ohm,
        "load_resistance_ohm",
    )

    thermal_variance_a2 = thermal_noise_variance(
        temperature_k=temperature_k,
        bandwidth_hz=bandwidth_hz,
        load_resistance_ohm=load_resistance_ohm,
    )

    zero_shot_variance_a2 = shot_noise_variance(
        signal_current_a=0.0,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
    )

    one_shot_variance_a2 = shot_noise_variance(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
    )

    zero_total_variance_a2 = total_noise_variance(
        shot_variance_a2=zero_shot_variance_a2,
        thermal_variance_a2=thermal_variance_a2,
    )

    one_total_variance_a2 = total_noise_variance(
        shot_variance_a2=one_shot_variance_a2,
        thermal_variance_a2=thermal_variance_a2,
    )

    return (
        zero_total_variance_a2,
        one_total_variance_a2,
    )


def midpoint_threshold(
    zero_level_a: float,
    one_level_a: float,
) -> float:
    """Calculate the midpoint decision threshold."""

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

    return (
        zero_level_a
        + one_level_a
    ) / 2.0


def detect_ook_samples(
    received_samples_a: Sequence[float],
    threshold_a: float,
) -> list[int]:
    """Detect OOK bits using a fixed current threshold."""

    if len(received_samples_a) == 0:
        raise ValueError(
            "received_samples_a must not be empty"
        )

    _require_finite(
        threshold_a,
        "threshold_a",
    )

    detected_bits: list[int] = []

    for index, sample_a in enumerate(
        received_samples_a
    ):
        _require_finite(
            sample_a,
            f"received_samples_a[{index}]",
        )

        detected_bits.append(
            1 if sample_a >= threshold_a else 0
        )

    return detected_bits


def bit_error_count(
    transmitted_bits: Sequence[int],
    detected_bits: Sequence[int],
) -> int:
    """Count bit disagreements between two binary sequences."""

    validate_bits(transmitted_bits)
    validate_bits(detected_bits)

    if len(transmitted_bits) != len(detected_bits):
        raise ValueError(
            "Bit sequences must have the same length"
        )

    return sum(
        transmitted_bit != detected_bit
        for transmitted_bit, detected_bit in zip(
            transmitted_bits,
            detected_bits,
            strict=True,
        )
    )


def bit_error_rate(
    transmitted_bits: Sequence[int],
    detected_bits: Sequence[int],
) -> float:
    """Calculate the measured bit-error rate."""

    errors = bit_error_count(
        transmitted_bits=transmitted_bits,
        detected_bits=detected_bits,
    )

    return errors / len(transmitted_bits)


def gaussian_tail_probability(
    value: float,
) -> float:
    """Return the upper-tail probability of a standard normal variable."""

    _require_finite(
        value,
        "value",
    )

    return (
        0.5
        * math.erfc(
            value / math.sqrt(2.0)
        )
    )


def theoretical_midpoint_ber(
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
) -> float:
    """Calculate midpoint-threshold BER for equally likely OOK bits.

    Separate zero-state and one-state noise variances are used.
    """

    zero_level_a, one_level_a = ook_current_levels(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
    )

    zero_variance_a2, one_variance_a2 = (
        ook_noise_variances(
            signal_current_a=signal_current_a,
            background_current_a=background_current_a,
            dark_current_a=dark_current_a,
            bandwidth_hz=bandwidth_hz,
            temperature_k=temperature_k,
            load_resistance_ohm=load_resistance_ohm,
        )
    )

    threshold_a = midpoint_threshold(
        zero_level_a=zero_level_a,
        one_level_a=one_level_a,
    )

    zero_standard_deviation_a = math.sqrt(
        zero_variance_a2
    )

    one_standard_deviation_a = math.sqrt(
        one_variance_a2
    )

    zero_error_probability = (
        gaussian_tail_probability(
            (
                threshold_a
                - zero_level_a
            )
            / zero_standard_deviation_a
        )
    )

    one_error_probability = (
        gaussian_tail_probability(
            (
                one_level_a
                - threshold_a
            )
            / one_standard_deviation_a
        )
    )

    return (
        zero_error_probability
        + one_error_probability
    ) / 2.0


def simulate_ook_detection(
    transmitted_bits: Sequence[int],
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
    seed: int | None = None,
) -> dict[
    str,
    float | int | list[int] | list[float],
]:
    """Simulate noisy OOK samples and threshold detection."""

    validate_bits(transmitted_bits)

    zero_level_a, one_level_a = ook_current_levels(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
    )

    zero_variance_a2, one_variance_a2 = (
        ook_noise_variances(
            signal_current_a=signal_current_a,
            background_current_a=background_current_a,
            dark_current_a=dark_current_a,
            bandwidth_hz=bandwidth_hz,
            temperature_k=temperature_k,
            load_resistance_ohm=load_resistance_ohm,
        )
    )

    threshold_a = midpoint_threshold(
        zero_level_a=zero_level_a,
        one_level_a=one_level_a,
    )

    zero_standard_deviation_a = math.sqrt(
        zero_variance_a2
    )

    one_standard_deviation_a = math.sqrt(
        one_variance_a2
    )

    random_generator = random.Random(seed)

    received_samples_a: list[float] = []

    for bit in transmitted_bits:
        if bit == 0:
            mean_current_a = zero_level_a
            standard_deviation_a = (
                zero_standard_deviation_a
            )
        else:
            mean_current_a = one_level_a
            standard_deviation_a = (
                one_standard_deviation_a
            )

        received_samples_a.append(
            random_generator.gauss(
                mean_current_a,
                standard_deviation_a,
            )
        )

    detected_bits = detect_ook_samples(
        received_samples_a=received_samples_a,
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
        "received_samples_a": (
            received_samples_a
        ),
        "detected_bits": detected_bits,
        "zero_level_a": zero_level_a,
        "one_level_a": one_level_a,
        "threshold_a": threshold_a,
        "zero_noise_variance_a2": (
            zero_variance_a2
        ),
        "one_noise_variance_a2": (
            one_variance_a2
        ),
        "error_count": error_count,
        "ber": measured_ber,
        "theoretical_ber": predicted_ber,
    }