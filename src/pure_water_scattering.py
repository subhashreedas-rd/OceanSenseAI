"""Models for molecular scattering by pure water."""

from math import isfinite, pi
from numbers import Real


BOLTZMANN_CONSTANT = 1.380649e-23


def cabannes_factor(delta: float) -> float:
    """Return the dimensionless Cabannes factor.

    Parameters
    ----------
    delta:
        Molecular depolarization ratio satisfying 0 <= delta < 6/7.
    """
    if isinstance(delta, bool) or not isinstance(delta, Real):
        raise TypeError("delta must be a real number")

    delta = float(delta)

    if not isfinite(delta):
        raise ValueError("delta must be finite")

    if not 0.0 <= delta < 6.0 / 7.0:
        raise ValueError("delta must satisfy 0 <= delta < 6/7")

    return (6.0 + 6.0 * delta) / (6.0 - 7.0 * delta)


def pmh_density_derivative(refractive_index: float) -> float:
    """Calculate the PMH density derivative of squared refractive index.

    Returns the dimensionless quantity:

        rho * (partial n^2 / partial rho)

    Parameters
    ----------
    refractive_index:
        Absolute refractive index of pure water in vacuum.
    """
    if (
        isinstance(refractive_index, bool)
        or not isinstance(refractive_index, Real)
    ):
        raise TypeError("refractive_index must be a real number")

    refractive_index = float(refractive_index)

    if not isfinite(refractive_index):
        raise ValueError("refractive_index must be finite")

    if refractive_index <= 1.0:
        raise ValueError("refractive_index must be greater than 1")

    n_squared = refractive_index**2

    return (n_squared - 1.0) * (
        1.0
        + (2.0 / 3.0)
        * (n_squared + 2.0)
        * ((n_squared - 1.0) / (3.0 * refractive_index)) ** 2
    )


def air_refractive_index(wavelength_nm: float) -> float:
    """Calculate the refractive index of standard air.

    Parameters
    ----------
    wavelength_nm:
        Vacuum wavelength in nanometres.
    """
    if isinstance(wavelength_nm, bool) or not isinstance(wavelength_nm, Real):
        raise TypeError("wavelength_nm must be a real number")

    wavelength_nm = float(wavelength_nm)

    if not isfinite(wavelength_nm):
        raise ValueError("wavelength_nm must be finite")

    if wavelength_nm <= 0.0:
        raise ValueError("wavelength_nm must be greater than zero")

    wavelength_um = wavelength_nm / 1000.0
    reciprocal_wavelength_squared = (1.0 / wavelength_um) ** 2

    k0 = 238.0185
    k1 = 5_792_105.0
    k2 = 57.362
    k3 = 167_917.0

    refractivity = (
        k1 / (k0 - reciprocal_wavelength_squared)
        + k3 / (k2 - reciprocal_wavelength_squared)
    )

    return 1.0 + refractivity * 1.0e-8


def pure_water_refractive_index(
    wavelength_nm: float,
    temperature_c: float,
) -> float:
    """Calculate the absolute refractive index of pure water.

    Parameters
    ----------
    wavelength_nm:
        Vacuum wavelength in nanometres, from 200 to 1100 nm.
    temperature_c:
        Water temperature in degrees Celsius.
    """
    if isinstance(wavelength_nm, bool) or not isinstance(wavelength_nm, Real):
        raise TypeError("wavelength_nm must be a real number")

    if isinstance(temperature_c, bool) or not isinstance(temperature_c, Real):
        raise TypeError("temperature_c must be a real number")

    wavelength_nm = float(wavelength_nm)
    temperature_c = float(temperature_c)

    if not isfinite(wavelength_nm):
        raise ValueError("wavelength_nm must be finite")

    if not isfinite(temperature_c):
        raise ValueError("temperature_c must be finite")

    if not 200.0 <= wavelength_nm <= 1100.0:
        raise ValueError("wavelength_nm must be between 200 and 1100 nm")

    n0 = 1.31405
    n4 = -2.02e-6
    n5 = 15.868
    n7 = -0.00423
    n8 = -4382.0
    n9 = 1.1455e6

    relative_refractive_index = (
        n0
        + n4 * temperature_c**2
        + (n5 + n7 * temperature_c) / wavelength_nm
        + n8 / wavelength_nm**2
        + n9 / wavelength_nm**3
    )

    return relative_refractive_index * air_refractive_index(wavelength_nm)


def isothermal_compressibility(temperature_c: float) -> float:
    """Calculate pure-water isothermal compressibility in Pa^-1.

    Parameters
    ----------
    temperature_c:
        Water temperature in degrees Celsius, from 0 to 110 °C.
    """
    if isinstance(temperature_c, bool) or not isinstance(temperature_c, Real):
        raise TypeError("temperature_c must be a real number")

    temperature_c = float(temperature_c)

    if not isfinite(temperature_c):
        raise ValueError("temperature_c must be finite")

    if not 0.0 <= temperature_c <= 110.0:
        raise ValueError("temperature_c must be between 0 and 110 °C")

    a0 = 50.88630
    a1 = 0.7171582
    a2 = 0.7819867e-3
    a3 = 31.62214e-6
    a4 = -0.1323594e-6
    a5 = 0.6345750e-9

    b0 = 1.0
    b1 = 21.65928e-3

    numerator = (
        a0
        + a1 * temperature_c
        + a2 * temperature_c**2
        + a3 * temperature_c**3
        + a4 * temperature_c**4
        + a5 * temperature_c**5
    )

    denominator = b0 + b1 * temperature_c

    compressibility_times_one_million = numerator / denominator

    return compressibility_times_one_million * 1.0e-11


def volume_scattering_90(
    wavelength_nm: float,
    temperature_c: float,
    delta: float = 0.039,
) -> float:
    """Calculate pure-water volume scattering at 90 degrees.

    Parameters
    ----------
    wavelength_nm:
        Vacuum wavelength in nanometres.
    temperature_c:
        Water temperature in degrees Celsius, from 0 to 110 °C.
    delta:
        Molecular depolarization ratio. The default is 0.039.

    Returns
    -------
    float
        Volume scattering function at 90 degrees in m^-1 sr^-1.
    """
    factor = cabannes_factor(delta)
    compressibility = isothermal_compressibility(temperature_c)

    refractive_index = pure_water_refractive_index(
        wavelength_nm,
        temperature_c,
    )

    density_derivative = pmh_density_derivative(refractive_index)

    wavelength_m = float(wavelength_nm) * 1.0e-9
    temperature_k = float(temperature_c) + 273.15

    return (
        pi**2
        / (2.0 * wavelength_m**4)
        * density_derivative**2
        * BOLTZMANN_CONSTANT
        * temperature_k
        * compressibility
        * factor
    )


def molecular_scattering_coefficient(
    wavelength_nm: float,
    temperature_c: float,
    delta: float = 0.039,
) -> float:
    """Calculate the total molecular scattering coefficient.

    The angular molecular-scattering function is integrated over
    the complete sphere to convert beta(90) into the total
    scattering coefficient.

    Parameters
    ----------
    wavelength_nm:
        Vacuum wavelength in nanometres.
    temperature_c:
        Water temperature in degrees Celsius.
    delta:
        Molecular depolarization ratio. The default is 0.039.

    Returns
    -------
    float
        Molecular scattering coefficient in m^-1.
    """
    beta_90 = volume_scattering_90(
        wavelength_nm,
        temperature_c,
        delta,
    )

    delta = float(delta)

    angular_integral = (
        (8.0 * pi / 3.0)
        * (2.0 + delta)
        / (1.0 + delta)
    )

    return beta_90 * angular_integral