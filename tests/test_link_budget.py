"""Unit tests for the baseline underwater optical link budget."""

from __future__ import annotations

import math
import unittest

from src.link_budget import (
    BOLTZMANN_CONSTANT,
    ELEMENTARY_CHARGE,
    beam_area,
    beam_radius,
    calculate_link_budget,
    electrical_snr,
    geometric_collection_efficiency,
    noise_rms_current,
    received_optical_power,
    receiver_area,
    shot_noise_variance,
    signal_photocurrent,
    snr_db,
    thermal_noise_variance,
    total_noise_variance,
    water_transmittance,
)


class TestLinkBudget(unittest.TestCase):
    """Verify the baseline optical receiver equations."""

    def test_beam_radius_at_zero_distance(self) -> None:
        result = beam_radius(
            distance_m=0.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.02,
        )

        self.assertAlmostEqual(
            result,
            0.01,
            places=15,
        )

    def test_beam_radius_increases_with_distance(self) -> None:
        near_radius = beam_radius(
            distance_m=1.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.01,
        )

        far_radius = beam_radius(
            distance_m=10.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.01,
        )

        self.assertGreater(
            far_radius,
            near_radius,
        )

    def test_beam_area(self) -> None:
        result = beam_area(
            beam_radius_m=2.0,
        )

        self.assertAlmostEqual(
            result,
            4.0 * math.pi,
            places=15,
        )

    def test_receiver_area(self) -> None:
        result = receiver_area(
            receiver_radius_m=0.5,
        )

        self.assertAlmostEqual(
            result,
            0.25 * math.pi,
            places=15,
        )

    def test_geometric_efficiency_area_ratio(self) -> None:
        result = geometric_collection_efficiency(
            beam_radius_m=0.10,
            receiver_radius_m=0.05,
        )

        self.assertAlmostEqual(
            result,
            0.25,
            places=15,
        )

    def test_geometric_efficiency_cannot_exceed_one(self) -> None:
        result = geometric_collection_efficiency(
            beam_radius_m=0.01,
            receiver_radius_m=0.02,
        )

        self.assertEqual(
            result,
            1.0,
        )

    def test_water_transmittance_at_zero_distance(self) -> None:
        result = water_transmittance(
            attenuation_per_m=0.2,
            distance_m=0.0,
        )

        self.assertEqual(
            result,
            1.0,
        )

    def test_water_transmittance_known_value(self) -> None:
        result = water_transmittance(
            attenuation_per_m=0.1,
            distance_m=10.0,
        )

        self.assertAlmostEqual(
            result,
            math.exp(-1.0),
            places=15,
        )

    def test_received_power_at_zero_distance(self) -> None:
        result = received_optical_power(
            transmitted_power_w=2.0,
            attenuation_per_m=0.0,
            distance_m=0.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.0,
            receiver_radius_m=0.02,
            system_efficiency=0.8,
        )

        self.assertAlmostEqual(
            result,
            1.6,
            places=15,
        )

    def test_received_power_decreases_with_distance(self) -> None:
        near_power = received_optical_power(
            transmitted_power_w=1.0,
            attenuation_per_m=0.05,
            distance_m=1.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.005,
            receiver_radius_m=0.02,
            system_efficiency=0.9,
        )

        far_power = received_optical_power(
            transmitted_power_w=1.0,
            attenuation_per_m=0.05,
            distance_m=20.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.005,
            receiver_radius_m=0.02,
            system_efficiency=0.9,
        )

        self.assertLess(
            far_power,
            near_power,
        )

    def test_zero_transmitted_power(self) -> None:
        result = received_optical_power(
            transmitted_power_w=0.0,
            attenuation_per_m=0.1,
            distance_m=10.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.01,
            receiver_radius_m=0.02,
            system_efficiency=0.8,
        )

        self.assertEqual(
            result,
            0.0,
        )

    def test_signal_photocurrent(self) -> None:
        result = signal_photocurrent(
            received_power_w=2.0e-3,
            responsivity_a_per_w=0.4,
        )

        self.assertAlmostEqual(
            result,
            8.0e-4,
            places=15,
        )

    def test_shot_noise_variance(self) -> None:
        signal_current = 1.0e-6
        background_current = 2.0e-7
        dark_current = 1.0e-9
        bandwidth = 1.0e6

        expected = (
            2.0
            * ELEMENTARY_CHARGE
            * (
                signal_current
                + background_current
                + dark_current
            )
            * bandwidth
        )

        result = shot_noise_variance(
            signal_current_a=signal_current,
            background_current_a=background_current,
            dark_current_a=dark_current,
            bandwidth_hz=bandwidth,
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=30,
        )

    def test_thermal_noise_variance(self) -> None:
        temperature = 300.0
        bandwidth = 1.0e6
        resistance = 1000.0

        expected = (
            4.0
            * BOLTZMANN_CONSTANT
            * temperature
            * bandwidth
            / resistance
        )

        result = thermal_noise_variance(
            temperature_k=temperature,
            bandwidth_hz=bandwidth,
            load_resistance_ohm=resistance,
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=30,
        )

    def test_total_noise_variance(self) -> None:
        result = total_noise_variance(
            shot_variance_a2=2.0e-15,
            thermal_variance_a2=3.0e-15,
        )

        self.assertAlmostEqual(
            result,
            5.0e-15,
            places=30,
        )

    def test_noise_rms_current(self) -> None:
        result = noise_rms_current(
            noise_variance_a2=9.0e-12,
        )

        self.assertAlmostEqual(
            result,
            3.0e-6,
            places=15,
        )

    def test_electrical_snr(self) -> None:
        result = electrical_snr(
            signal_current_a=2.0e-6,
            noise_variance_a2=1.0e-12,
        )

        self.assertAlmostEqual(
            result,
            4.0,
            places=15,
        )

    def test_snr_decibel_conversion(self) -> None:
        result = snr_db(
            snr_linear=100.0,
        )

        self.assertAlmostEqual(
            result,
            20.0,
            places=15,
        )

    def test_complete_link_budget(self) -> None:
        result = calculate_link_budget(
            transmitted_power_w=1.0,
            attenuation_per_m=0.02,
            distance_m=10.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.005,
            receiver_radius_m=0.025,
            system_efficiency=0.8,
            responsivity_a_per_w=0.4,
            background_power_w=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
        )

        self.assertGreater(
            result["received_power_w"],
            0.0,
        )

        self.assertGreater(
            result["signal_current_a"],
            0.0,
        )

        self.assertGreater(
            result["total_noise_variance_a2"],
            0.0,
        )

        self.assertGreater(
            result["snr_linear"],
            0.0,
        )

        self.assertAlmostEqual(
            result["snr_db"],
            10.0
            * math.log10(result["snr_linear"]),
            places=12,
        )

    def test_zero_power_complete_link_budget(self) -> None:
        result = calculate_link_budget(
            transmitted_power_w=0.0,
            attenuation_per_m=0.02,
            distance_m=10.0,
            initial_beam_radius_m=0.01,
            divergence_half_angle_rad=0.005,
            receiver_radius_m=0.025,
            system_efficiency=0.8,
            responsivity_a_per_w=0.4,
            background_power_w=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
        )

        self.assertEqual(
            result["received_power_w"],
            0.0,
        )

        self.assertEqual(
            result["signal_current_a"],
            0.0,
        )

        self.assertEqual(
            result["snr_linear"],
            0.0,
        )

        self.assertEqual(
            result["snr_db"],
            -math.inf,
        )

    def test_invalid_negative_distance(self) -> None:
        with self.assertRaises(ValueError):
            beam_radius(
                distance_m=-1.0,
                initial_beam_radius_m=0.01,
                divergence_half_angle_rad=0.01,
            )

    def test_invalid_system_efficiency(self) -> None:
        with self.assertRaises(ValueError):
            received_optical_power(
                transmitted_power_w=1.0,
                attenuation_per_m=0.1,
                distance_m=1.0,
                initial_beam_radius_m=0.01,
                divergence_half_angle_rad=0.01,
                receiver_radius_m=0.02,
                system_efficiency=1.1,
            )


if __name__ == "__main__":
    unittest.main()