"""Photon-budget calculations for underwater optical links.

This module connects received optical power to mean photon numbers.
It does not simulate individual photon detections or a security protocol.
"""

from __future__ import annotations

import math


# Exact SI constants
PLANCK_CONSTANT_J_S = 6.62607015e-34
SPEED_OF_LIGHT_M_S = 299_792_458.0


def _require_finite_nonnegative(value: float, name: str) -> float:
    """Return value as a float after checking that it is finite and nonnegative."""
    value = float(value)

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")

    if value < 0.0:
        raise ValueError(f"{name} must be nonnegative.")

    return value


def _require_finite_positive(value: float, name: str) -> float:
    """Return value as a float after checking that it is finite and positive."""
    value = float(value)

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")

    if value <= 0.0:
        raise ValueError(f"{name} must be greater than zero.")

    return value


def photon_energy_joule(wavelength_nm: float) -> float:
    """Calculate the energy of one photon.

    Parameters
    ----------
    wavelength_nm:
        Optical wavelength in nanometres.

    Returns
    -------
    float
        Energy of one photon in joules.

    Notes
    -----
    The calculation uses

        E = h c / wavelength
    """
    wavelength_nm = _require_finite_positive(
        wavelength_nm,
        "wavelength_nm",
    )
    wavelength_m = wavelength_nm * 1.0e-9

    return (
        PLANCK_CONSTANT_J_S
        * SPEED_OF_LIGHT_M_S
        / wavelength_m
    )


def received_energy_joule(
    received_power_w: float,
    interval_s: float,
) -> float:
    """Calculate optical energy received during a time interval.

    Parameters
    ----------
    received_power_w:
        Received optical power in watts.
    interval_s:
        Observation, pulse, or bit duration in seconds.

    Returns
    -------
    float
        Received optical energy in joules.

    Notes
    -----
    The calculation uses

        E_received = P_received * interval
    """
    received_power_w = _require_finite_nonnegative(
        received_power_w,
        "received_power_w",
    )
    interval_s = _require_finite_positive(
        interval_s,
        "interval_s",
    )

    return received_power_w * interval_s


def mean_received_photons(
    received_power_w: float,
    interval_s: float,
    wavelength_nm: float,
) -> float:
    """Calculate the mean number of photons received during an interval.

    Parameters
    ----------
    received_power_w:
        Received optical power in watts.
    interval_s:
        Observation, pulse, or bit duration in seconds.
    wavelength_nm:
        Optical wavelength in nanometres.

    Returns
    -------
    float
        Mean number of received photons.

    Notes
    -----
    The calculation uses

        mean_photons = received_energy / photon_energy

    This result is an expected photon number and does not need to be
    an integer.
    """
    energy_received = received_energy_joule(
        received_power_w,
        interval_s,
    )
    energy_per_photon = photon_energy_joule(wavelength_nm)

    return energy_received / energy_per_photon


def mean_detected_photons(
    mean_received: float,
    detector_efficiency: float,
) -> float:
    """Calculate the mean number of detected photons.

    Parameters
    ----------
    mean_received:
        Mean number of photons incident on the detector.
    detector_efficiency:
        Probability of detecting an incident photon, from 0 to 1.

    Returns
    -------
    float
        Mean number of detected photons.

    Notes
    -----
    The calculation uses

        mean_detected = detector_efficiency * mean_received
    """
    mean_received = _require_finite_nonnegative(
        mean_received,
        "mean_received",
    )
    detector_efficiency = _require_finite_nonnegative(
        detector_efficiency,
        "detector_efficiency",
    )

    if detector_efficiency > 1.0:
        raise ValueError(
            "detector_efficiency must be between 0 and 1."
        )

    return detector_efficiency * mean_received


def mean_photons_per_bit(
    received_power_w: float,
    bit_rate_bps: float,
    wavelength_nm: float,
) -> float:
    """Calculate the mean received photon number per bit.

    Parameters
    ----------
    received_power_w:
        Received optical power in watts.
    bit_rate_bps:
        Bit rate in bits per second.
    wavelength_nm:
        Optical wavelength in nanometres.

    Returns
    -------
    float
        Mean number of received photons during one bit period.
    """
    bit_rate_bps = _require_finite_positive(
        bit_rate_bps,
        "bit_rate_bps",
    )
    bit_duration_s = 1.0 / bit_rate_bps

    return mean_received_photons(
        received_power_w=received_power_w,
        interval_s=bit_duration_s,
        wavelength_nm=wavelength_nm,
    )