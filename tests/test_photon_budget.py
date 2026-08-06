"""Tests for photon-budget calculations."""

from __future__ import annotations

import math
import unittest

from src.photon_budget import (
    mean_detected_photons,
    mean_photons_per_bit,
    mean_received_photons,
    photon_energy_joule,
    received_energy_joule,
)


class TestPhotonEnergy(unittest.TestCase):
    """Tests for the energy of one photon."""

    def test_photon_energy_at_500_nm(self) -> None:
        """A 500 nm photon should have the expected energy."""
        result = photon_energy_joule(500.0)
        expected = 3.972891714297857e-19

        self.assertAlmostEqual(result, expected, places=30)

    def test_shorter_wavelength_has_greater_energy(self) -> None:
        """Photon energy should decrease as wavelength increases."""
        energy_400_nm = photon_energy_joule(400.0)
        energy_800_nm = photon_energy_joule(800.0)

        self.assertGreater(energy_400_nm, energy_800_nm)

    def test_doubling_wavelength_halves_energy(self) -> None:
        """Photon energy is inversely proportional to wavelength."""
        energy_400_nm = photon_energy_joule(400.0)
        energy_800_nm = photon_energy_joule(800.0)

        self.assertAlmostEqual(
            energy_400_nm / energy_800_nm,
            2.0,
            places=12,
        )

    def test_zero_wavelength_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            photon_energy_joule(0.0)

    def test_negative_wavelength_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            photon_energy_joule(-500.0)

    def test_nonfinite_wavelength_is_rejected(self) -> None:
        for value in (math.inf, -math.inf, math.nan):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    photon_energy_joule(value)


class TestReceivedEnergy(unittest.TestCase):
    """Tests for optical energy accumulated over an interval."""

    def test_received_energy_equals_power_times_time(self) -> None:
        result = received_energy_joule(
            received_power_w=2.0,
            interval_s=0.5,
        )

        self.assertEqual(result, 1.0)

    def test_zero_power_gives_zero_energy(self) -> None:
        result = received_energy_joule(
            received_power_w=0.0,
            interval_s=1.0,
        )

        self.assertEqual(result, 0.0)

    def test_negative_power_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            received_energy_joule(
                received_power_w=-1.0,
                interval_s=1.0,
            )

    def test_nonpositive_interval_is_rejected(self) -> None:
        for value in (0.0, -1.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    received_energy_joule(
                        received_power_w=1.0,
                        interval_s=value,
                    )


class TestMeanPhotonNumbers(unittest.TestCase):
    """Tests for mean received and detected photon numbers."""

    def test_mean_received_photons_known_case(self) -> None:
        """Check a known power, duration, and wavelength calculation."""
        result = mean_received_photons(
            received_power_w=1.0e-9,
            interval_s=1.0e-6,
            wavelength_nm=500.0,
        )
        expected = 2517.058283771355

        self.assertAlmostEqual(result, expected, places=9)

    def test_zero_received_power_gives_zero_photons(self) -> None:
        result = mean_received_photons(
            received_power_w=0.0,
            interval_s=1.0e-6,
            wavelength_nm=500.0,
        )

        self.assertEqual(result, 0.0)

    def test_detected_photons_apply_efficiency(self) -> None:
        result = mean_detected_photons(
            mean_received=100.0,
            detector_efficiency=0.25,
        )

        self.assertEqual(result, 25.0)

    def test_zero_efficiency_gives_zero_detected_photons(self) -> None:
        result = mean_detected_photons(
            mean_received=100.0,
            detector_efficiency=0.0,
        )

        self.assertEqual(result, 0.0)

    def test_unit_efficiency_preserves_received_mean(self) -> None:
        result = mean_detected_photons(
            mean_received=100.0,
            detector_efficiency=1.0,
        )

        self.assertEqual(result, 100.0)

    def test_efficiency_above_one_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mean_detected_photons(
                mean_received=100.0,
                detector_efficiency=1.01,
            )

    def test_negative_mean_received_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            mean_detected_photons(
                mean_received=-1.0,
                detector_efficiency=0.5,
            )

    def test_photons_per_bit_matches_direct_interval_calculation(
        self,
    ) -> None:
        power_w = 2.0e-9
        bit_rate_bps = 20.0e6
        wavelength_nm = 500.0

        result = mean_photons_per_bit(
            received_power_w=power_w,
            bit_rate_bps=bit_rate_bps,
            wavelength_nm=wavelength_nm,
        )

        expected = mean_received_photons(
            received_power_w=power_w,
            interval_s=1.0 / bit_rate_bps,
            wavelength_nm=wavelength_nm,
        )

        self.assertAlmostEqual(result, expected, places=12)

    def test_nonpositive_bit_rate_is_rejected(self) -> None:
        for value in (0.0, -1.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    mean_photons_per_bit(
                        received_power_w=1.0,
                        bit_rate_bps=value,
                        wavelength_nm=500.0,
                    )


if __name__ == "__main__":
    unittest.main()