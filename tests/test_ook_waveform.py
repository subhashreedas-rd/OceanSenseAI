"""Unit tests for sampled OOK waveform processing."""

from __future__ import annotations

import math
import unittest

from src.ook import generate_bits
from src.ook_waveform import (
    add_state_dependent_waveform_noise,
    decision_sample_indices,
    extract_matched_filter_decisions,
    generate_rectangular_ook_waveform,
    integrate_and_dump,
    rectangular_matched_filter,
    sample_noise_variance,
    simulate_sampled_ook,
)


class TestOOKWaveform(unittest.TestCase):
    """Verify sampled OOK generation and detection."""

    def test_generate_rectangular_waveform(self) -> None:
        result = generate_rectangular_ook_waveform(
            bits=[0, 1, 0],
            zero_level_a=1.0,
            one_level_a=3.0,
            samples_per_bit=3,
        )

        self.assertEqual(
            result,
            [
                1.0,
                1.0,
                1.0,
                3.0,
                3.0,
                3.0,
                1.0,
                1.0,
                1.0,
            ],
        )

    def test_waveform_length(self) -> None:
        bits = [0, 1, 1, 0]

        result = generate_rectangular_ook_waveform(
            bits=bits,
            zero_level_a=2.0e-9,
            one_level_a=5.0e-6,
            samples_per_bit=8,
        )

        self.assertEqual(
            len(result),
            len(bits) * 8,
        )

    def test_waveform_rejects_invalid_bit(self) -> None:
        with self.assertRaises(ValueError):
            generate_rectangular_ook_waveform(
                bits=[0, 1, 2],
                zero_level_a=0.0,
                one_level_a=1.0,
                samples_per_bit=4,
            )

    def test_waveform_rejects_invalid_samples_per_bit(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            generate_rectangular_ook_waveform(
                bits=[0, 1],
                zero_level_a=0.0,
                one_level_a=1.0,
                samples_per_bit=0,
            )

    def test_sample_noise_variance_scaling(self) -> None:
        result = sample_noise_variance(
            decision_noise_variance_a2=2.0e-12,
            samples_per_bit=8,
        )

        self.assertAlmostEqual(
            result,
            1.6e-11,
            places=25,
        )

    def test_zero_variance_noise_preserves_waveform(
        self,
    ) -> None:
        bits = [0, 1, 1, 0]

        clean_waveform = (
            generate_rectangular_ook_waveform(
                bits=bits,
                zero_level_a=1.0,
                one_level_a=5.0,
                samples_per_bit=3,
            )
        )

        noisy_waveform = (
            add_state_dependent_waveform_noise(
                bits=bits,
                clean_waveform_a=clean_waveform,
                zero_decision_variance_a2=0.0,
                one_decision_variance_a2=0.0,
                samples_per_bit=3,
                seed=10,
            )
        )

        self.assertEqual(
            noisy_waveform,
            clean_waveform,
        )

    def test_waveform_noise_is_reproducible(self) -> None:
        bits = [0, 1, 0, 1]

        clean_waveform = (
            generate_rectangular_ook_waveform(
                bits=bits,
                zero_level_a=1.0e-9,
                one_level_a=1.0e-6,
                samples_per_bit=4,
            )
        )

        first_result = (
            add_state_dependent_waveform_noise(
                bits=bits,
                clean_waveform_a=clean_waveform,
                zero_decision_variance_a2=1.0e-14,
                one_decision_variance_a2=2.0e-14,
                samples_per_bit=4,
                seed=100,
            )
        )

        second_result = (
            add_state_dependent_waveform_noise(
                bits=bits,
                clean_waveform_a=clean_waveform,
                zero_decision_variance_a2=1.0e-14,
                one_decision_variance_a2=2.0e-14,
                samples_per_bit=4,
                seed=100,
            )
        )

        self.assertEqual(
            first_result,
            second_result,
        )

    def test_waveform_noise_rejects_length_mismatch(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            add_state_dependent_waveform_noise(
                bits=[0, 1],
                clean_waveform_a=[0.0, 0.0, 1.0],
                zero_decision_variance_a2=1.0e-12,
                one_decision_variance_a2=1.0e-12,
                samples_per_bit=2,
            )

    def test_rectangular_filter_constant_input(
        self,
    ) -> None:
        result = rectangular_matched_filter(
            received_waveform_a=[
                4.0,
                4.0,
                4.0,
                4.0,
                4.0,
            ],
            samples_per_bit=3,
        )

        self.assertEqual(
            result,
            [
                4.0,
                4.0,
                4.0,
                4.0,
                4.0,
            ],
        )

    def test_rectangular_filter_decision_values(
        self,
    ) -> None:
        waveform = [
            1.0,
            1.0,
            1.0,
            3.0,
            3.0,
            3.0,
        ]

        filtered = rectangular_matched_filter(
            received_waveform_a=waveform,
            samples_per_bit=3,
        )

        decisions = (
            extract_matched_filter_decisions(
                filtered_waveform_a=filtered,
                number_of_bits=2,
                samples_per_bit=3,
            )
        )

        self.assertEqual(
            decisions,
            [1.0, 3.0],
        )

    def test_decision_sample_indices(self) -> None:
        result = decision_sample_indices(
            number_of_bits=4,
            samples_per_bit=3,
        )

        self.assertEqual(
            result,
            [2, 5, 8, 11],
        )

    def test_extract_decisions_rejects_wrong_length(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            extract_matched_filter_decisions(
                filtered_waveform_a=[
                    1.0,
                    2.0,
                    3.0,
                ],
                number_of_bits=2,
                samples_per_bit=2,
            )

    def test_integrate_and_dump(self) -> None:
        result = integrate_and_dump(
            received_waveform_a=[
                1.0,
                3.0,
                5.0,
                7.0,
            ],
            samples_per_bit=2,
        )

        self.assertEqual(
            result,
            [2.0, 6.0],
        )

    def test_integrate_and_dump_rejects_partial_bit(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            integrate_and_dump(
                received_waveform_a=[
                    1.0,
                    2.0,
                    3.0,
                ],
                samples_per_bit=2,
            )

    def test_complete_simulation_is_reproducible(
        self,
    ) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=200,
            seed=12,
        )

        first_result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=8,
            seed=50,
        )

        second_result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=2.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=8,
            seed=50,
        )

        self.assertEqual(
            first_result["noisy_waveform_a"],
            second_result["noisy_waveform_a"],
        )

        self.assertEqual(
            first_result["detected_bits"],
            second_result["detected_bits"],
        )

    def test_complete_simulation_output_lengths(
        self,
    ) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=100,
            seed=25,
        )

        samples_per_bit = 6

        result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=5.0e-7,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=100.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=samples_per_bit,
            seed=26,
        )

        expected_waveform_length = (
            len(transmitted_bits)
            * samples_per_bit
        )

        self.assertEqual(
            len(result["clean_waveform_a"]),
            expected_waveform_length,
        )

        self.assertEqual(
            len(result["noisy_waveform_a"]),
            expected_waveform_length,
        )

        self.assertEqual(
            len(result["filtered_waveform_a"]),
            expected_waveform_length,
        )

        self.assertEqual(
            len(result["decision_samples_a"]),
            len(transmitted_bits),
        )

        self.assertEqual(
            len(result["detected_bits"]),
            len(transmitted_bits),
        )

    def test_high_signal_simulation_has_no_errors(
        self,
    ) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=1000,
            seed=70,
        )

        result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=1.0e-4,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=1.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=8,
            seed=71,
        )

        self.assertEqual(
            result["error_count"],
            0,
        )

        self.assertEqual(
            result["ber"],
            0.0,
        )

    def test_complete_simulation_returns_valid_ber(
        self,
    ) -> None:
        transmitted_bits = generate_bits(
            number_of_bits=2000,
            seed=90,
        )

        result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=5.0e-7,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=100.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=8,
            seed=91,
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

    def test_sample_variance_matches_scaling_rule(
        self,
    ) -> None:
        transmitted_bits = [0, 1, 0, 1]

        result = simulate_sampled_ook(
            transmitted_bits=transmitted_bits,
            signal_current_a=1.0e-6,
            background_current_a=1.0e-9,
            dark_current_a=1.0e-9,
            bandwidth_hz=10.0e6,
            temperature_k=300.0,
            load_resistance_ohm=1000.0,
            samples_per_bit=5,
            seed=123,
        )

        self.assertAlmostEqual(
            result["zero_sample_variance_a2"],
            result["zero_decision_variance_a2"]
            * 5,
            places=30,
        )

        self.assertAlmostEqual(
            result["one_sample_variance_a2"],
            result["one_decision_variance_a2"]
            * 5,
            places=30,
        )


if __name__ == "__main__":
    unittest.main()