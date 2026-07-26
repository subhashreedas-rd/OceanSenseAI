"""Tests for the pure-water molecular-scattering functions."""

import math
import unittest

from src.pure_water_scattering import (
    air_refractive_index,
    cabannes_factor,
    isothermal_compressibility,
    pmh_density_derivative,
    pure_water_refractive_index,
    volume_scattering_90,
)


class TestCabannesFactor(unittest.TestCase):
    """Tests for the Cabannes-factor calculation."""

    def test_zero_depolarization(self) -> None:
        self.assertEqual(cabannes_factor(0.0), 1.0)

    def test_reference_value(self) -> None:
        result = cabannes_factor(0.039)
        self.assertAlmostEqual(result, 1.088528025, places=9)

    def test_increases_with_delta(self) -> None:
        self.assertGreater(
            cabannes_factor(0.051),
            cabannes_factor(0.039),
        )

    def test_negative_delta_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cabannes_factor(-0.01)

    def test_upper_limit_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cabannes_factor(6.0 / 7.0)

    def test_nonfinite_values_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    cabannes_factor(value)

    def test_non_numeric_value_rejected(self) -> None:
        with self.assertRaises(TypeError):
            cabannes_factor("0.039")  # type: ignore[arg-type]

    def test_boolean_rejected(self) -> None:
        with self.assertRaises(TypeError):
            cabannes_factor(True)


class TestPMHDensityDerivative(unittest.TestCase):
    """Tests for the PMH density-derivative calculation."""

    def test_reference_value(self) -> None:
        result = pmh_density_derivative(1.333)
        self.assertAlmostEqual(result, 0.850716314, places=9)

    def test_increases_with_refractive_index(self) -> None:
        self.assertGreater(
            pmh_density_derivative(1.34),
            pmh_density_derivative(1.33),
        )

    def test_refractive_index_equal_to_one_rejected(self) -> None:
        with self.assertRaises(ValueError):
            pmh_density_derivative(1.0)

    def test_refractive_index_below_one_rejected(self) -> None:
        with self.assertRaises(ValueError):
            pmh_density_derivative(0.99)

    def test_nonfinite_values_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    pmh_density_derivative(value)

    def test_non_numeric_value_rejected(self) -> None:
        with self.assertRaises(TypeError):
            pmh_density_derivative("1.333")  # type: ignore[arg-type]

    def test_boolean_rejected(self) -> None:
        with self.assertRaises(TypeError):
            pmh_density_derivative(True)


class TestAirRefractiveIndex(unittest.TestCase):
    """Tests for the refractive index of standard air."""

    def test_reference_value_at_532_nm(self) -> None:
        result = air_refractive_index(532.0)
        self.assertAlmostEqual(result, 1.000278208318, places=12)

    def test_decreases_with_wavelength(self) -> None:
        self.assertGreater(
            air_refractive_index(400.0),
            air_refractive_index(700.0),
        )

    def test_zero_wavelength_rejected(self) -> None:
        with self.assertRaises(ValueError):
            air_refractive_index(0.0)

    def test_negative_wavelength_rejected(self) -> None:
        with self.assertRaises(ValueError):
            air_refractive_index(-532.0)

    def test_nonfinite_values_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    air_refractive_index(value)

    def test_non_numeric_value_rejected(self) -> None:
        with self.assertRaises(TypeError):
            air_refractive_index("532")  # type: ignore[arg-type]

    def test_boolean_rejected(self) -> None:
        with self.assertRaises(TypeError):
            air_refractive_index(True)


class TestPureWaterRefractiveIndex(unittest.TestCase):
    """Tests for the absolute refractive index of pure water."""

    def test_reference_value_at_532_nm_and_20_c(self) -> None:
        result = pure_water_refractive_index(532.0, 20.0)
        self.assertAlmostEqual(result, 1.335406496503, places=12)

    def test_decreases_with_wavelength(self) -> None:
        self.assertGreater(
            pure_water_refractive_index(400.0, 20.0),
            pure_water_refractive_index(700.0, 20.0),
        )

    def test_decreases_with_temperature(self) -> None:
        self.assertGreater(
            pure_water_refractive_index(532.0, 20.0),
            pure_water_refractive_index(532.0, 25.0),
        )

    def test_wavelength_outside_model_range_rejected(self) -> None:
        for wavelength in (199.0, 1101.0):
            with self.subTest(wavelength=wavelength):
                with self.assertRaises(ValueError):
                    pure_water_refractive_index(wavelength, 20.0)

    def test_nonfinite_wavelength_rejected(self) -> None:
        for wavelength in (math.nan, math.inf, -math.inf):
            with self.subTest(wavelength=wavelength):
                with self.assertRaises(ValueError):
                    pure_water_refractive_index(wavelength, 20.0)

    def test_nonfinite_temperature_rejected(self) -> None:
        for temperature in (math.nan, math.inf, -math.inf):
            with self.subTest(temperature=temperature):
                with self.assertRaises(ValueError):
                    pure_water_refractive_index(532.0, temperature)

    def test_non_numeric_inputs_rejected(self) -> None:
        with self.assertRaises(TypeError):
            pure_water_refractive_index(
                "532",
                20.0,
            )  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            pure_water_refractive_index(
                532.0,
                "20",
            )  # type: ignore[arg-type]

    def test_boolean_inputs_rejected(self) -> None:
        with self.assertRaises(TypeError):
            pure_water_refractive_index(True, 20.0)

        with self.assertRaises(TypeError):
            pure_water_refractive_index(532.0, True)


class TestIsothermalCompressibility(unittest.TestCase):
    """Tests for pure-water isothermal compressibility."""

    def test_reference_value_at_20_c(self) -> None:
        result = isothermal_compressibility(20.0)
        self.assertAlmostEqual(result, 4.58950249960647e-10, places=21)

    def test_result_is_positive(self) -> None:
        self.assertGreater(isothermal_compressibility(20.0), 0.0)

    def test_value_changes_with_temperature(self) -> None:
        self.assertGreater(
            isothermal_compressibility(20.0),
            isothermal_compressibility(50.0),
        )

    def test_temperature_range_boundaries_accepted(self) -> None:
        self.assertGreater(isothermal_compressibility(0.0), 0.0)
        self.assertGreater(isothermal_compressibility(110.0), 0.0)

    def test_temperature_outside_range_rejected(self) -> None:
        for temperature in (-0.1, 110.1):
            with self.subTest(temperature=temperature):
                with self.assertRaises(ValueError):
                    isothermal_compressibility(temperature)

    def test_nonfinite_temperature_rejected(self) -> None:
        for temperature in (math.nan, math.inf, -math.inf):
            with self.subTest(temperature=temperature):
                with self.assertRaises(ValueError):
                    isothermal_compressibility(temperature)

    def test_non_numeric_temperature_rejected(self) -> None:
        with self.assertRaises(TypeError):
            isothermal_compressibility("20")  # type: ignore[arg-type]

    def test_boolean_temperature_rejected(self) -> None:
        with self.assertRaises(TypeError):
            isothermal_compressibility(True)


class TestVolumeScattering90(unittest.TestCase):
    """Tests for the pure-water volume scattering function."""

    def test_reference_value_at_532_nm_and_20_c(self) -> None:
        result = volume_scattering_90(532.0, 20.0)
        self.assertAlmostEqual(result, 9.188096537574e-05, places=15)

    def test_matches_pmh_reference_table(self) -> None:
        reference_values = {
            366.0: 4.500e-4,
            405.0: 2.903e-4,
            436.0: 2.120e-4,
            546.0: 0.824e-4,
            578.0: 0.650e-4,
        }

        for wavelength, expected in reference_values.items():
            with self.subTest(wavelength=wavelength):
                result = volume_scattering_90(
                    wavelength,
                    20.0,
                    delta=0.039,
                )
                self.assertAlmostEqual(
                    result,
                    expected,
                    delta=5.0e-7,
                )

    def test_decreases_with_wavelength(self) -> None:
        self.assertGreater(
            volume_scattering_90(400.0, 20.0),
            volume_scattering_90(700.0, 20.0),
        )

    def test_result_is_positive(self) -> None:
        self.assertGreater(
            volume_scattering_90(532.0, 20.0),
            0.0,
        )

    def test_wavelength_outside_model_range_rejected(self) -> None:
        for wavelength in (199.0, 1101.0):
            with self.subTest(wavelength=wavelength):
                with self.assertRaises(ValueError):
                    volume_scattering_90(wavelength, 20.0)

    def test_temperature_outside_model_range_rejected(self) -> None:
        for temperature in (-0.1, 110.1):
            with self.subTest(temperature=temperature):
                with self.assertRaises(ValueError):
                    volume_scattering_90(532.0, temperature)

    def test_invalid_depolarization_ratio_rejected(self) -> None:
        for delta in (-0.001, 6.0 / 7.0):
            with self.subTest(delta=delta):
                with self.assertRaises(ValueError):
                    volume_scattering_90(
                        532.0,
                        20.0,
                        delta=delta,
                    )


if __name__ == "__main__":
    unittest.main()