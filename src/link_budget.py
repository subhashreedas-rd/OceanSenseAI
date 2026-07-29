"""Baseline underwater optical receiver and link-budget equations.

This module keeps water attenuation, geometric collection, detector
conversion, and electrical noise as separate physical components.
"""

from __future__ import annotations

import math


BOLTZMANN_CONSTANT = 1.380649e-23
ELEMENTARY_CHARGE = 1.602176634e-19


def _require_non_negative(
    value: float,
    name: str,
) -> None:
    """Require a finite value greater than or equal to zero."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")


def _require_positive(
    value: float,
    name: str,
) -> None:
    """Require a finite value greater than zero."""

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def beam_radius(
    distance_m: float,
    initial_beam_radius_m: float,
    divergence_half_angle_rad: float,
) -> float:
    """Calculate beam radius using a simple expanding-beam model.

    The divergence input is the beam half-angle in radians.

    The model is:

        w(L) = w0 + L tan(theta)
    """

    _require_non_negative(
        distance_m,
        "distance_m",
    )

    _require_positive(
        initial_beam_radius_m,
        "initial_beam_radius_m",
    )

    _require_non_negative(
        divergence_half_angle_rad,
        "divergence_half_angle_rad",
    )

    if divergence_half_angle_rad >= math.pi / 2.0:
        raise ValueError(
            "divergence_half_angle_rad must be less than pi/2"
        )

    radius_m = (
        initial_beam_radius_m
        + distance_m
        * math.tan(divergence_half_angle_rad)
    )

    if not math.isfinite(radius_m):
        raise ValueError(
            "Calculated beam radius must be finite"
        )

    return radius_m


def beam_area(
    beam_radius_m: float,
) -> float:
    """Calculate the area of a circular beam footprint."""

    _require_positive(
        beam_radius_m,
        "beam_radius_m",
    )

    return math.pi * beam_radius_m**2


def receiver_area(
    receiver_radius_m: float,
) -> float:
    """Calculate the area of a circular receiver aperture."""

    _require_positive(
        receiver_radius_m,
        "receiver_radius_m",
    )

    return math.pi * receiver_radius_m**2


def geometric_collection_efficiency(
    beam_radius_m: float,
    receiver_radius_m: float,
) -> float:
    """Calculate centred collection for a uniform circular beam.

    The receiver and beam are assumed to be perfectly aligned.

    The result is limited to the physical interval 0 to 1.
    """

    beam_footprint_area = beam_area(
        beam_radius_m=beam_radius_m,
    )

    aperture_area = receiver_area(
        receiver_radius_m=receiver_radius_m,
    )

    efficiency = (
        aperture_area
        / beam_footprint_area
    )

    return min(
        1.0,
        max(0.0, efficiency),
    )


def water_transmittance(
    attenuation_per_m: float,
    distance_m: float,
) -> float:
    """Calculate Beer-Lambert water transmittance."""

    _require_non_negative(
        attenuation_per_m,
        "attenuation_per_m",
    )

    _require_non_negative(
        distance_m,
        "distance_m",
    )

    return math.exp(
        -attenuation_per_m * distance_m
    )


def received_optical_power(
    transmitted_power_w: float,
    attenuation_per_m: float,
    distance_m: float,
    initial_beam_radius_m: float,
    divergence_half_angle_rad: float,
    receiver_radius_m: float,
    system_efficiency: float = 1.0,
) -> float:
    """Calculate optical power collected by the receiver.

    The implemented relationship is:

        Pr = Pt * eta_system * eta_geometric * exp(-cL)
    """

    _require_non_negative(
        transmitted_power_w,
        "transmitted_power_w",
    )

    _require_non_negative(
        system_efficiency,
        "system_efficiency",
    )

    if system_efficiency > 1.0:
        raise ValueError(
            "system_efficiency must not exceed 1"
        )

    radius_m = beam_radius(
        distance_m=distance_m,
        initial_beam_radius_m=initial_beam_radius_m,
        divergence_half_angle_rad=(
            divergence_half_angle_rad
        ),
    )

    geometric_efficiency = (
        geometric_collection_efficiency(
            beam_radius_m=radius_m,
            receiver_radius_m=receiver_radius_m,
        )
    )

    channel_transmittance = water_transmittance(
        attenuation_per_m=attenuation_per_m,
        distance_m=distance_m,
    )

    return (
        transmitted_power_w
        * system_efficiency
        * geometric_efficiency
        * channel_transmittance
    )


def signal_photocurrent(
    received_power_w: float,
    responsivity_a_per_w: float,
) -> float:
    """Convert received optical power into signal photocurrent."""

    _require_non_negative(
        received_power_w,
        "received_power_w",
    )

    _require_non_negative(
        responsivity_a_per_w,
        "responsivity_a_per_w",
    )

    return (
        responsivity_a_per_w
        * received_power_w
    )


def background_photocurrent(
    background_power_w: float,
    responsivity_a_per_w: float,
) -> float:
    """Convert background optical power into photocurrent."""

    return signal_photocurrent(
        received_power_w=background_power_w,
        responsivity_a_per_w=responsivity_a_per_w,
    )


def shot_noise_variance(
    signal_current_a: float,
    background_current_a: float,
    dark_current_a: float,
    bandwidth_hz: float,
) -> float:
    """Calculate shot-noise current variance.

    The model is:

        sigma_shot^2
        = 2 q (Is + Ibg + Id) B
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

    total_detector_current_a = (
        signal_current_a
        + background_current_a
        + dark_current_a
    )

    return (
        2.0
        * ELEMENTARY_CHARGE
        * total_detector_current_a
        * bandwidth_hz
    )


def thermal_noise_variance(
    temperature_k: float,
    bandwidth_hz: float,
    load_resistance_ohm: float,
) -> float:
    """Calculate Johnson-Nyquist current-noise variance.

    The model is:

        sigma_thermal^2 = 4 k T B / R
    """

    _require_positive(
        temperature_k,
        "temperature_k",
    )

    _require_positive(
        bandwidth_hz,
        "bandwidth_hz",
    )

    _require_positive(
        load_resistance_ohm,
        "load_resistance_ohm",
    )

    return (
        4.0
        * BOLTZMANN_CONSTANT
        * temperature_k
        * bandwidth_hz
        / load_resistance_ohm
    )


def total_noise_variance(
    shot_variance_a2: float,
    thermal_variance_a2: float,
) -> float:
    """Combine independent shot- and thermal-noise variances."""

    _require_non_negative(
        shot_variance_a2,
        "shot_variance_a2",
    )

    _require_non_negative(
        thermal_variance_a2,
        "thermal_variance_a2",
    )

    return (
        shot_variance_a2
        + thermal_variance_a2
    )


def noise_rms_current(
    noise_variance_a2: float,
) -> float:
    """Convert current-noise variance into RMS current."""

    _require_non_negative(
        noise_variance_a2,
        "noise_variance_a2",
    )

    return math.sqrt(
        noise_variance_a2
    )


def electrical_snr(
    signal_current_a: float,
    noise_variance_a2: float,
) -> float:
    """Calculate current-domain electrical SNR."""

    _require_non_negative(
        signal_current_a,
        "signal_current_a",
    )

    _require_positive(
        noise_variance_a2,
        "noise_variance_a2",
    )

    return (
        signal_current_a**2
        / noise_variance_a2
    )


def snr_db(
    snr_linear: float,
) -> float:
    """Convert positive linear SNR into decibels."""

    _require_positive(
        snr_linear,
        "snr_linear",
    )

    return (
        10.0
        * math.log10(snr_linear)
    )


def calculate_link_budget(
    transmitted_power_w: float,
    attenuation_per_m: float,
    distance_m: float,
    initial_beam_radius_m: float,
    divergence_half_angle_rad: float,
    receiver_radius_m: float,
    system_efficiency: float,
    responsivity_a_per_w: float,
    background_power_w: float,
    dark_current_a: float,
    bandwidth_hz: float,
    temperature_k: float,
    load_resistance_ohm: float,
) -> dict[str, float]:
    """Calculate the complete baseline receiver link budget."""

    radius_m = beam_radius(
        distance_m=distance_m,
        initial_beam_radius_m=initial_beam_radius_m,
        divergence_half_angle_rad=(
            divergence_half_angle_rad
        ),
    )

    geometric_efficiency = (
        geometric_collection_efficiency(
            beam_radius_m=radius_m,
            receiver_radius_m=receiver_radius_m,
        )
    )

    transmittance = water_transmittance(
        attenuation_per_m=attenuation_per_m,
        distance_m=distance_m,
    )

    received_power_w = received_optical_power(
        transmitted_power_w=transmitted_power_w,
        attenuation_per_m=attenuation_per_m,
        distance_m=distance_m,
        initial_beam_radius_m=initial_beam_radius_m,
        divergence_half_angle_rad=(
            divergence_half_angle_rad
        ),
        receiver_radius_m=receiver_radius_m,
        system_efficiency=system_efficiency,
    )

    signal_current_a = signal_photocurrent(
        received_power_w=received_power_w,
        responsivity_a_per_w=responsivity_a_per_w,
    )

    background_current_a = background_photocurrent(
        background_power_w=background_power_w,
        responsivity_a_per_w=responsivity_a_per_w,
    )

    shot_variance_a2 = shot_noise_variance(
        signal_current_a=signal_current_a,
        background_current_a=background_current_a,
        dark_current_a=dark_current_a,
        bandwidth_hz=bandwidth_hz,
    )

    thermal_variance_a2 = thermal_noise_variance(
        temperature_k=temperature_k,
        bandwidth_hz=bandwidth_hz,
        load_resistance_ohm=load_resistance_ohm,
    )

    total_variance_a2 = total_noise_variance(
        shot_variance_a2=shot_variance_a2,
        thermal_variance_a2=thermal_variance_a2,
    )

    signal_to_noise_ratio = electrical_snr(
        signal_current_a=signal_current_a,
        noise_variance_a2=total_variance_a2,
    )

    signal_to_noise_ratio_db = (
        snr_db(signal_to_noise_ratio)
        if signal_to_noise_ratio > 0.0
        else -math.inf
    )

    return {
        "distance_m": distance_m,
        "beam_radius_m": radius_m,
        "geometric_collection_efficiency": (
            geometric_efficiency
        ),
        "water_transmittance": transmittance,
        "received_power_w": received_power_w,
        "signal_current_a": signal_current_a,
        "background_current_a": background_current_a,
        "shot_noise_variance_a2": shot_variance_a2,
        "thermal_noise_variance_a2": (
            thermal_variance_a2
        ),
        "total_noise_variance_a2": total_variance_a2,
        "noise_rms_current_a": noise_rms_current(
            total_variance_a2
        ),
        "snr_linear": signal_to_noise_ratio,
        "snr_db": signal_to_noise_ratio_db,
    }       