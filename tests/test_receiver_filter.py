"""Unit tests for bandwidth-limited OOK receiver processing."""

from __future__ import annotations

import math
import unittest

from src.ook import generate_bits
from src.receiver_filter import (
    add_decision_noise,
    calculate_eye_metrics,
    decision_sample_indices,
    extract_decision_samples,
    first_order_lowpass_alpha,
    first_order_lowpass_filter,
    simulate_bandlimited_ook,
)


class TestReceiverFilter(unittest.TestCase):
    """Verify receiver filtering, sampling, eye metrics, and BER."""

    def test_lowpass_alpha_matches_equation(self) -> None:
        cutoff_hz = 1.0e6
        sample_rate_hz = 10.0e6

        expected = (
            1.0
            - math.exp(
                -2.0
                * math.pi
                * cutoff_hz
                / sample_rate_hz
            )
        )

        result = first_order_lowpass_alpha(
            cutoff_hz=cutoff_hz,
            sample_rate_hz=sample_rate_hz,
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=15,
        )

    def test_lowpass_alpha_is_between_zero_and_one(
        self,
    ) -> None:
        result = first_order_lowpass_alpha(
            cutoff_hz=1.0e6,
            sample_rate_hz=20.0e6,
        )

        self.assertGreater(
            result,
            0.0,
        )

        self.assertLess(
            result,
            1.0,
        )

    def test_lowpass_alpha_rejects_nyquist_cutoff(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            first_order_lowpass_alpha(
                cutoff_hz=5.0e6,
                sample_rate_hz=10.0e6,
            )

    def test_lowpass_filter_constant_input(self) -> None:
        result = first_order_lowpass_filter(
            samples=[
                3.0,
                3.0,
                3.0,
                3.0,
            ],
            cutoff_hz=1.0e6,
            sample_rate_hz=10.0e6,
        )

        for value in result:
            self.assertAlmostEqual(
                value,
                3.0,
                places=15,
            )

    def test_lowpass_filter_step_response_rises(
        self,
    ) -> None:
        result = first_order_lowpass_filter(
            samples=[
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
            ],
            cutoff_hz=1.0e6,
            sample_rate_hz=10.0e6,
            initial_output=0.0,
        )

        self.assertEqual(
            result[0],
            0.0,
        )

        self.assertGreater(
            result[2],
            0.0,
        )

        self.assertLess(
            result[2],
            1.0,
        )

        self.assertGreater(
            result[3],
            result[2],
        )

        self.assertGreater(
            result[4],
            result[3],
        )

        self.assertLess(
            result[4],
            1.0,
        )

    def test_lowpass_filter_step_response_falls(
        self,
    ) -> None:
        result = first_order_lowpass_filter(
            samples=[
                1.0,
                1.0,
                0.0,
                0.0,
                0.0,
            ],
            cutoff_hz=1.0e6,
            sample_rate_hz=10.0e6,
            initial_output=1.0,
        )

        self.assertLess(
            result[2],
            1.0,
        )

        self.assertGreater(
            result[2],
            0.0,
        )

        self.assertLess(
            result[3],
            result[2],
        )

        self.assertLess(
            result[4],
            result[3],
        )

    def test_decision_indices_at_end_of_bit(self) -> None:
        result = decision_sample_indices(
            number_of_bits=4,
            samples_per_bit=8,
            sampling_fraction=1.0,
        )

        self.assertEqual(
            result,
            [7, 15, 23, 31],
        )

    def test_decision_indices_at_half_bit(self) -> None:
        result = decision_sample_indices(
            number_of_bits=3,
            samples_per_bit=8,
            sampling_fraction=0.5,
        )

        self.assertEqual(
            result,
            [3, 11, 19],
        )

    def test_decision_indices_reject_fraction_above_one(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            decision_sample_indices(
                number_of_bits=2,
                samples_per_bit=8,
                sampling_fraction=1.1,
            )

    def test_extract_decision_samples(self) -> None:
        waveform = [
            0.0,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            6.0,
            7.0,
        ]

        result = extract_decision_samples(
            waveform_a=waveform,
            number_of_bits=2,
            samples_per_bit=4,
            sampling_fraction=1.0,
        )

        self.assertEqual(
            result,
            [3.0, 7.0],
        )

    def test_extract_decisions_rejects_wrong_length(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            extract_decision_samples(
                waveform_a=[
                    0.0,
                    1.0,
                    2.0,
                ],
                number_of_bits=2,
                samples_per_bit=2,
                sampling_fraction=1.0,
            )

    def test_zero_variance_decision_noise_preserves_samples(
        self,
    ) -> None:
        clean_samples = [
            1.0,
            5.0,
            1.0,
            5.0,
        ]

        result = add_decision_noise(
            transmitted_bits=[
                0,
                1,
                0,
                1,
            ],
            clean_decision_samples_a=clean_samples,
            zero_noise_variance_a2=0.0,
            one_noise_variance_a2=0.0,
            seed=10,
        )

        self.assertEqual(
            result,
            clean_samples,
        )

    def test_decision_noise_is_reproducible(self) -> None:
        bits = [
            0,
            1,
            0,
            1,
        ]

        clean_samples = [
            1.0e-9,
            1.0e-6,
            1.0e-9,
            1.0e-6,
        ]

        first_result = add_decision_noise(
            transmitted_bits=bits,
            clean_decision_samples_a=clean_samples,
            zero_noise_variance_a2=1.0e-14,
            one_noise_variance_a2=2.0e-14,
            seed=100,
        )

        second_result = add_decision_noise(
            transmitted_bits=bits,
            clean_decision_samples_a=clean_samples,
            zero_noise_variance_a2=1.0e-14,
            one_noise_variance_a2=2.0e-14,
            seed=100,
        )

        self.assertEqual(
            first_result,
            second_result,
        )

    def test_eye_metrics_for_ideal_levels(self) -> None:
        result = calculate_eye_metrics(
            transmitted_bits=[
                0,
                1,
                0,
                1,
            ],
            clean_decision_samples_a=[
                2.0e-9,
                1.002e-6,
                2.0e-9,
                1.002e-6,
            ],
            nominal_signal_current_a=1.0e-6,
        )

        self.assertAlmostEqual(
            result["maximum_zero_a"],
            2.0e-9,
            places=18,
        )

        self.assertAlmostEqual(
            result["minimum_one_a"],
            1.002e-6,
            places=18,
        )

        self.assertAlmostEqual(
            result["eye_opening_a"],
            1.0e-6,
            places=18,
        )

        self.assertAlmostEqual(
            result["normalized_eye_opening"],
            1.0,
            places=15,
        )

    def test_eye_metrics_detect_closed_eye(self) -> None:
        result = calculate_eye_metrics(
            transmitted_bits=[
                0,
                1,
                0,
                1,
            ],
            clean_decision_samples_a=[
                0.6,
                0.4,
                0.7,
                0.5,
            ],
            nominal_signal_current_a=1.0,
        )

        self.assertLess(
            result["eye_opening_a"],
            0.0,
        )

        self.assertLess(
            result["normalized_eye_opening"],
            0.0,
        )

    def test_complete_simulation_is_reproducible(
        self,
    ) -> None:
        bits = generate_bits(
            number_of_bits=500,
            seed=50,
        )

        first_result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=1.0e6,
            receiver_cutoff_hz=1.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=200,
        )

        second_result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=1.0e6,
            receiver_cutoff_hz=1.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=200,
        )

        self.assertEqual(
            first_result["noisy_decision_samples_a"],
            second_result["noisy_decision_samples_a"],
        )

        self.assertEqual(
            first_result["detected_bits"],
            second_result["detected_bits"],
        )

    def test_complete_simulation_output_lengths(
        self,
    ) -> None:
        bits = generate_bits(
            number_of_bits=100,
            seed=70,
        )

        samples_per_bit = 12

        result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=5.0e-7,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=100.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=10.0e6,
            receiver_cutoff_hz=3.0e6,
            samples_per_bit=samples_per_bit,
            sampling_fraction=1.0,
            seed=71,
        )

        expected_waveform_length = (
            len(bits)
            * samples_per_bit
        )

        self.assertEqual(
            len(result["clean_waveform_a"]),
            expected_waveform_length,
        )

        self.assertEqual(
            len(result["filtered_waveform_a"]),
            expected_waveform_length,
        )

        self.assertEqual(
            len(result["clean_decision_samples_a"]),
            len(bits),
        )

        self.assertEqual(
            len(result["noisy_decision_samples_a"]),
            len(bits),
        )

        self.assertEqual(
            len(result["detected_bits"]),
            len(bits),
        )

    def test_high_bandwidth_preserves_large_eye_opening(
        self,
    ) -> None:
        bits = [
            0,
            1,
            0,
            1,
        ] * 100

        result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=1.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=1.0e6,
            receiver_cutoff_hz=4.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=90,
        )

        self.assertGreater(
            result["normalized_eye_opening"],
            0.95,
        )

    def test_low_bandwidth_reduces_eye_opening(
        self,
    ) -> None:
        bits = [
            0,
            1,
            0,
            1,
        ] * 100

        high_bandwidth_result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=1.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=10.0e6,
            receiver_cutoff_hz=30.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=100,
        )

        low_bandwidth_result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=1.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=10.0e6,
            receiver_cutoff_hz=1.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=100,
        )

        self.assertLess(
            low_bandwidth_result[
                "normalized_eye_opening"
            ],
            high_bandwidth_result[
                "normalized_eye_opening"
            ],
        )

    def test_complete_simulation_returns_valid_ber(
        self,
    ) -> None:
        bits = generate_bits(
            number_of_bits=2000,
            seed=120,
        )

        result = simulate_bandlimited_ook(
            transmitted_bits=bits,
            signal_current_a=5.0e-7,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=100.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            bit_rate_hz=20.0e6,
            receiver_cutoff_hz=5.0e6,
            samples_per_bit=16,
            sampling_fraction=1.0,
            seed=121,
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
            result["ideal_no_isi_ber"],
            0.0,
        )

        self.assertLessEqual(
            result["ideal_no_isi_ber"],
            0.5,
        )

        self.assertTrue(
            math.isfinite(
                result["normalized_eye_opening"]
            )
        )


if __name__ == "__main__":
    unittest.main()