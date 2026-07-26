"""Tests for the total pure-water molecular scattering coefficient."""

import math
import unittest

from src.pure_water_scattering import (
    molecular_scattering_coefficient,
    volume_scattering_90,
)


class TestMolecularScatteringCoefficient(unittest.TestCase):
    """Tests for the integrated molecular scattering coefficient."""

    def test_reference_value_at_532_nm_and_20_c(self) -> None:
        result = molecular_scattering_coefficient(532.0, 20.0)

        self.assertAlmostEqual(
            result,
            0.001510587312738,
            places=15,
        )

    def test_matches_angular_integration(self) -> None:
        delta = 0.039

        beta_90 = volume_scattering_90(
            532.0,
            20.0,
            delta,
        )

        expected = (
            beta_90
            * (8.0 * math.pi / 3.0)
            * (2.0 + delta)
            / (1.0 + delta)
        )

        result = molecular_scattering_coefficient(
            532.0,
            20.0,
            delta,
        )

        self.assertAlmostEqual(result, expected, places=15)

    def test_result_is_positive(self) -> None:
        result = molecular_scattering_coefficient(532.0, 20.0)

        self.assertGreater(result, 0.0)

    def test_decreases_with_wavelength(self) -> None:
        shorter_wavelength = molecular_scattering_coefficient(
            400.0,
            20.0,
        )

        longer_wavelength = molecular_scattering_coefficient(
            700.0,
            20.0,
        )

        self.assertGreater(
            shorter_wavelength,
            longer_wavelength,
        )

    def test_invalid_wavelength_rejected(self) -> None:
        for wavelength in (199.0, 1101.0):
            with self.subTest(wavelength=wavelength):
                with self.assertRaises(ValueError):
                    molecular_scattering_coefficient(
                        wavelength,
                        20.0,
                    )

    def test_invalid_temperature_rejected(self) -> None:
        for temperature in (-0.1, 110.1):
            with self.subTest(temperature=temperature):
                with self.assertRaises(ValueError):
                    molecular_scattering_coefficient(
                        532.0,
                        temperature,
                    )

    def test_invalid_depolarization_ratio_rejected(self) -> None:
        for delta in (-0.001, 6.0 / 7.0):
            with self.subTest(delta=delta):
                with self.assertRaises(ValueError):
                    molecular_scattering_coefficient(
                        532.0,
                        20.0,
                        delta,
                    )


if __name__ == "__main__":
    unittest.main()