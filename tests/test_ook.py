"""Unit tests for current-domain on-off keying."""

from __future__ import annotations

import math
import unittest

from src.ook import (
    bit_error_count,
    bit_error_rate,
    detect_ook_samples,
    gaussian_tail_probability,
    generate_bits,
    midpoint_threshold,
    ook_current_levels,
    ook_noise_variances,
    simulate_ook_detection,
    theoretical_midpoint_ber,
    validate_bits,
)


class TestOOK(unittest.TestCase):
    """Verify OOK generation, noise, detection, and BER."""

    def test_validate_bits_accepts_binary_sequence(self) -> None:
        validate_bits([0, 1, 1, 0, 1])

    def test_validate_bits_rejects_empty_sequence(self) -> None:
        with self.assertRaises(ValueError):
            validate_bits([])

    def test_validate_bits_rejects_non_binary_value(self) -> None:
        with self.assertRaises(ValueError):
            validate_bits([0, 1, 2, 0])

    def test_generate_bits_returns_requested_length(self) -> None:
        bits = generate_bits(
            number_of_bits=100,
            seed=42,
        )

        self.assertEqual(
            len(bits),
            100,
        )

        self.assertTrue(
            all(bit in (0, 1) for bit in bits)
        )

    def test_generate_bits_is_reproducible(self) -> None:
        first_bits = generate_bits(
            number_of_bits=64,
            seed=1234,
        )

        second_bits = generate_bits(
            number_of_bits=64,
            seed=1234,
        )

        self.assertEqual(
            first_bits,
            second_bits,
        )

    def test_generate_bits_rejects_non_positive_length(self) -> None:
        with self.assertRaises(ValueError):
            generate_bits(
                number_of_bits=0,
            )

    def test_current_levels(self) -> None:
        zero_level, one_level = ook_current_levels(
            signal_current_a=5.0e-6,
            background_current_a=2.0e-7,
            dark_current_a=1.0e-9,
        )

        self.assertAlmostEqual(
            zero_level,
            2.01e-7,
            places=18,
        )

        self.assertAlmostEqual(
            one_level,
            5.201e-6,
            places=18,
        )

    def test_one_state_noise_exceeds_zero_state_noise(self) -> None:
        zero_variance, one_variance = (
            ook_noise_variances(
                signal_current_a=1.0e-5,
                background_current_a=1.0e-7,
                dark_current_a=1.0e-9,
                bandwidth_hz=1.0e6,
                temperature_k=300.0,
                load_resistance_ohm=1000.0,
            )
        )

        self.assertGreater(
            one_variance,
            zero_variance,
        )

    def test_midpoint_threshold(self) -> None:
        threshold = midpoint_threshold(
            zero_level_a=2.0e-6,
            one_level_a=8.0e-6,
        )

        self.assertAlmostEqual(
            threshold,
            5.0e-6,
            places=18,
        )

    def test_detect_ook_samples(self) -> None:
        detected = detect_ook_samples(
            received_samples_a=[
                0.1,
                0.7,
                0.5,
                0.49,
            ],
            threshold_a=0.5,
        )

        self.assertEqual(
            detected,
            [0, 1, 1, 0],
        )

    def test_bit_error_count(self) -> None:
        errors = bit_error_count(
            transmitted_bits=[0, 1, 1, 0],
            detected_bits=[0, 0, 1, 1],
        )

        self.assertEqual(
            errors,
            2,
        )

    def test_bit_error_rate(self) -> None:
        result = bit_error_rate(
            transmitted_bits=[0, 1, 1, 0],
            detected_bits=[0, 0, 1, 1],
        )

        self.assertEqual(
            result,
            0.5,
        )

    def test_bit_error_functions_reject_length_mismatch(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            bit_error_count(
                transmitted_bits=[0, 1],
                detected_bits=[0],
            )

    def test_standard_normal_tail_at_zero(self) -> None:
        probability = gaussian_tail_probability(
            0.0
        )

        self.assertEqual(
            probability,
            0.5,
        )

    def test_standard_normal_tail_decreases(self) -> None:
        probability_at_one = (
            gaussian_tail_probability(1.0)
        )

        probability_at_two = (
            gaussian_tail_probability(2.0)
        )

        self.assertLess(
            probability_at_two,
            probability_at_one,
        )

    def test_zero_signal_theoretical_ber_is_half(self) -> None:
        result = theoretical_midpoint_ber(
            signal_current_a=0.0,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
        )

        self.assertAlmostEqual(
            result,
            0.5,
            places=15,
        )

    def test_large_signal_theoretical_ber_is_small(self) -> None:
        result = theoretical_midpoint_ber(
            signal_current_a=1.0e-4,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
        )

        self.assertLess(
            result,
            1.0e-12,
        )

    def test_simulation_is_reproducible(self) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=100,
            seed=50,
        )

        first_result = simulate_ook_detection(
            transmitted_bits=transmitted_bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            seed=900,
        )

        second_result = simulate_ook_detection(
            transmitted_bits=transmitted_bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            seed=900,
        )

        self.assertEqual(
            first_result["received_samples_a"],
            second_result["received_samples_a"],
        )

        self.assertEqual(
            first_result["detected_bits"],
            second_result["detected_bits"],
        )

    def test_high_signal_simulation_has_no_errors(self) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=1000,
            seed=88,
        )

        result = simulate_ook_detection(
            transmitted_bits=transmitted_bits,
            signal_current_a=1.0e-4,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            seed=99,
        )

        self.assertEqual(
            result["error_count"],
            0,
        )

        self.assertEqual(
            result["ber"],
            0.0,
        )

    def test_simulation_returns_valid_values(self) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=500,
            seed=17,
        )

        result = simulate_ook_detection(
            transmitted_bits=transmitted_bits,
            signal_current_a=5.0e-7,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=100.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            seed=18,
        )

        self.assertEqual(
            len(result["detected_bits"]),
            len(transmitted_bits),
        )

        self.assertEqual(
            len(result["received_samples_a"]),
            len(transmitted_bits),
        )

        self.assertGreaterEqual(
            result["ber"],
            0.0,
        )

        self.assertLessEqual(
            result["ber"],
            1.0,
        )

        self.assertGreaterEqual(
            result["theoretical_ber"],
            0.0,
        )

        self.assertLessEqual(
            result["theoretical_ber"],
            0.5,
        )

        self.assertTrue(
            math.isfinite(result["threshold_a"])
        )


if __name__ == "__main__":
    unittest.main()