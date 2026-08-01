"""Bandwidth-limited receiver filtering for sampled OOK signals.

The model applies a first-order low-pass receiver response to the clean
rectangular OOK waveform. Receiver decision noise is then added at the
sampling instant using the noise variances established by the verified
receiver model.

This separates:

    deterministic pulse distortion and intersymbol interference

from:

    detector and electronics decision noise
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
from src.ook_waveform import (
    generate_rectangular_ook_waveform,
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


def _require_positive(
    value: float,
    name: str,
) -> None:
    """Require a finite value greater than zero."""

    _require_finite(value, name)

    if value <= 0.0:
        raise ValueError(
            f"{name} must be positive"
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


def first_order_lowpass_alpha(
    cutoff_hz: float,
    sample_rate_hz: float,
) -> float:
    """Return the discrete first-order low-pass coefficient.

    The coefficient is based on the exact sampled response of a
    continuous first-order system:

        alpha = 1 - exp(-2 pi fc / fs)
    """

    _require_positive(
        cutoff_hz,
        "cutoff_hz",
    )

    _require_positive(
        sample_rate_hz,
        "sample_rate_hz",
    )

    nyquist_hz = sample_rate_hz / 2.0

    if cutoff_hz >= nyquist_hz:
        raise ValueError(
            "cutoff_hz must be below half the sample rate"
        )

    return (
        1.0
        - math.exp(
            -2.0
            * math.pi
            * cutoff_hz
            / sample_rate_hz
        )
    )


def first_order_lowpass_filter(
    samples: Sequence[float],
    cutoff_hz: float,
    sample_rate_hz: float,
    initial_output: float | None = None,
) -> list[float]:
    """Apply a causal first-order low-pass filter."""

    if len(samples) == 0:
        raise ValueError(
            "samples must not be empty"
        )

    alpha = first_order_lowpass_alpha(
        cutoff_hz=cutoff_hz,
        sample_rate_hz=sample_rate_hz,
    )

    for index, sample in enumerate(samples):
        _require_finite(
            sample,
            f"samples[{index}]",
        )

    if initial_output is None:
        previous_output = float(samples[0])
    else:
        _require_finite(
            initial_output,
            "initial_output",
        )

        previous_output = initial_output

    filtered_samples: list[float] = []

    for sample in samples:
        previous_output = (
            previous_output
            + alpha
            * (
                sample
                - previous_output
            )
        )

        filtered_samples.append(
            previous_output
        )

    return filtered_samples


def decision_sample_indices(
    number_of_bits: int,
    samples_per_bit: int,
    sampling_fraction: float,
) -> list[int]:
    """Return one sampling index inside each bit interval.

    A sampling fraction of 1.0 selects the final sample of each bit.
    A sampling fraction of 0.5 selects approximately the bit centre.
    """

    _require_positive_integer(
        number_of_bits,
        "number_of_bits",
    )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    _require_positive(
        sampling_fraction,
        "sampling_fraction",
    )

    if sampling_fraction > 1.0:
        raise ValueError(
            "sampling_fraction must not exceed 1"
        )

    sample_offset = (
        math.ceil(
            sampling_fraction
            * samples_per_bit
        )
        - 1
    )

    sample_offset = min(
        samples_per_bit - 1,
        max(0, sample_offset),
    )

    return [
        (
            bit_index
            * samples_per_bit
            + sample_offset
        )
        for bit_index in range(number_of_bits)
    ]


def extract_decision_samples(
    waveform_a: Sequence[float],
    number_of_bits: int,
    samples_per_bit: int,
    sampling_fraction: float,
) -> list[float]:
    """Extract one receiver sample from each bit interval."""

    required_length = (
        number_of_bits
        * samples_per_bit
    )

    if len(waveform_a) != required_length:
        raise ValueError(
            "waveform_a length must equal "
            "number_of_bits * samples_per_bit"
        )

    indices = decision_sample_indices(
        number_of_bits=number_of_bits,
        samples_per_bit=samples_per_bit,
        sampling_fraction=sampling_fraction,
    )

    return [
        waveform_a[index]
        for index in indices
    ]


def add_decision_noise(
    transmitted_bits: Sequence[int],
    clean_decision_samples_a: Sequence[float],
    zero_noise_variance_a2: float,
    one_noise_variance_a2: float,
    seed: int | None = None,
) -> list[float]:
    """Add state-dependent Gaussian noise to decision samples."""

    validate_bits(transmitted_bits)

    if (
        len(clean_decision_samples_a)
        != len(transmitted_bits)
    ):
        raise ValueError(
            "clean_decision_samples_a and transmitted_bits "
            "must have equal lengths"
        )

    _require_non_negative(
        zero_noise_variance_a2,
        "zero_noise_variance_a2",
    )

    _require_non_negative(
        one_noise_variance_a2,
        "one_noise_variance_a2",
    )

    zero_standard_deviation_a = math.sqrt(
        zero_noise_variance_a2
    )

    one_standard_deviation_a = math.sqrt(
        one_noise_variance_a2
    )

    random_generator = random.Random(seed)

    noisy_samples_a: list[float] = []

    for index, (
        bit,
        clean_sample_a,
    ) in enumerate(
        zip(
            transmitted_bits,
            clean_decision_samples_a,
            strict=True,
        )
    ):
        _require_finite(
            clean_sample_a,
            f"clean_decision_samples_a[{index}]",
        )

        standard_deviation_a = (
            one_standard_deviation_a
            if bit == 1
            else zero_standard_deviation_a
        )

        noisy_samples_a.append(
            random_generator.gauss(
                clean_sample_a,
                standard_deviation_a,
            )
        )

    return noisy_samples_a


def calculate_eye_metrics(
    transmitted_bits: Sequence[int],
    clean_decision_samples_a: Sequence[float],
    nominal_signal_current_a: float,
) -> dict[str, float]:
    """Calculate noiseless decision-level separation metrics."""

    validate_bits(transmitted_bits)

    if (
        len(clean_decision_samples_a)
        != len(transmitted_bits)
    ):
        raise ValueError(
            "clean_decision_samples_a and transmitted_bits "
            "must have equal lengths"
        )

    _require_non_negative(
        nominal_signal_current_a,
        "nominal_signal_current_a",
    )

    zero_samples = [
        sample
        for bit, sample in zip(
            transmitted_bits,
            clean_decision_samples_a,
            strict=True,
        )
        if bit == 0
    ]

    one_samples = [
        sample
        for bit, sample in zip(
            transmitted_bits,
            clean_decision_samples_a,
            strict=True,
        )
        if bit == 1
    ]

    if not zero_samples or not one_samples:
        raise ValueError(
            "Both zero and one bits are required "
            "for eye metrics"
        )

    maximum_zero_a = max(zero_samples)
    minimum_one_a = min(one_samples)

    eye_opening_a = (
        minimum_one_a
        - maximum_zero_a
    )

    mean_zero_a = (
        sum(zero_samples)
        / len(zero_samples)
    )

    mean_one_a = (
        sum(one_samples)
        / len(one_samples)
    )

    mean_level_separation_a = (
        mean_one_a
        - mean_zero_a
    )

    if nominal_signal_current_a > 0.0:
        normalized_eye_opening = (
            eye_opening_a
            / nominal_signal_current_a
        )
    else:
        normalized_eye_opening = 0.0

    return {
        "maximum_zero_a": maximum_zero_a,
        "minimum_one_a": minimum_one_a,
        "mean_zero_a": mean_zero_a,
        "mean_one_a": mean_one_a,
        "eye_opening_a": eye_opening_a,
        "mean_level_separation_a": (
            mean_level_separation_a
        ),
        "normalized_eye_opening": (
            normalized_eye_opening
        ),
    }


def simulate_bandlimited_ook(
    transmitted_bits: Sequence[int],
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
    bit_rate_hz: float,
    receiver_cutoff_hz: float,
    samples_per_bit: int,
    sampling_fraction: float = 1.0,
    seed: int | None = None,
) -> dict[
    str,
    float | int | list[int] | list[float],
]:
    """Simulate OOK with first-order receiver bandwidth limitation."""

    validate_bits(transmitted_bits)

    _require_non_negative(
        signal_current_a,
        "signal_current_a",
    )

    _require_positive(
        bit_rate_hz,
        "bit_rate_hz",
    )

    _require_positive(
        receiver_cutoff_hz,
        "receiver_cutoff_hz",
    )

    _require_positive_integer(
        samples_per_bit,
        "samples_per_bit",
    )

    sample_rate_hz = (
        bit_rate_hz
        * samples_per_bit
    )

    zero_level_a, one_level_a = (
        ook_current_levels(
            signal_current_a=signal_current_a,
            background_current_a=background_current_a,
            dark_current_a=dark_current_a,
        )
    )

    zero_noise_variance_a2, (
        one_noise_variance_a2
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

    filtered_waveform_a = (
        first_order_lowpass_filter(
            samples=clean_waveform_a,
            cutoff_hz=receiver_cutoff_hz,
            sample_rate_hz=sample_rate_hz,
            initial_output=zero_level_a,
        )
    )

    clean_decision_samples_a = (
        extract_decision_samples(
            waveform_a=filtered_waveform_a,
            number_of_bits=len(
                transmitted_bits
            ),
            samples_per_bit=samples_per_bit,
            sampling_fraction=sampling_fraction,
        )
    )

    noisy_decision_samples_a = (
        add_decision_noise(
            transmitted_bits=transmitted_bits,
            clean_decision_samples_a=(
                clean_decision_samples_a
            ),
            zero_noise_variance_a2=(
                zero_noise_variance_a2
            ),
            one_noise_variance_a2=(
                one_noise_variance_a2
            ),
            seed=seed,
        )
    )

    threshold_a = midpoint_threshold(
        zero_level_a=zero_level_a,
        one_level_a=one_level_a,
    )

    detected_bits = detect_ook_samples(
        received_samples_a=(
            noisy_decision_samples_a
        ),
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

    ideal_no_isi_ber = theoretical_midpoint_ber(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
        temperature_k=temperature_k,
        load_resistance_ohm=load_resistance_ohm,
    )

    eye_metrics = calculate_eye_metrics(
        transmitted_bits=transmitted_bits,
        clean_decision_samples_a=(
            clean_decision_samples_a
        ),
        nominal_signal_current_a=signal_current_a,
    )

    return {
        "transmitted_bits": list(
            transmitted_bits
        ),
        "clean_waveform_a": clean_waveform_a,
        "filtered_waveform_a": (
            filtered_waveform_a
        ),
        "clean_decision_samples_a": (
            clean_decision_samples_a
        ),
        "noisy_decision_samples_a": (
            noisy_decision_samples_a
        ),
        "detected_bits": detected_bits,
        "samples_per_bit": samples_per_bit,
        "sample_rate_hz": sample_rate_hz,
        "bit_rate_hz": bit_rate_hz,
        "receiver_cutoff_hz": (
            receiver_cutoff_hz
        ),
        "sampling_fraction": sampling_fraction,
        "zero_level_a": zero_level_a,
        "one_level_a": one_level_a,
        "threshold_a": threshold_a,
        "zero_noise_variance_a2": (
            zero_noise_variance_a2
        ),
        "one_noise_variance_a2": (
            one_noise_variance_a2
        ),
        "error_count": error_count,
        "ber": measured_ber,
        "ideal_no_isi_ber": ideal_no_isi_ber,
        **eye_metrics,
    }