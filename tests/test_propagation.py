import math
import unittest

from src.propagation import (
    calculate_loss_db,
    calculate_transmittance,
    load_benchmark,
)


class TestPropagationModel(unittest.TestCase):
    def test_zero_distance_gives_full_transmittance(self) -> None:
        result = calculate_transmittance(
            attenuation_per_m=0.5,
            distance_m=0.0,
        )

        self.assertEqual(result, 1.0)

    def test_zero_attenuation_gives_full_transmittance(self) -> None:
        result = calculate_transmittance(
            attenuation_per_m=0.0,
            distance_m=100.0,
        )

        self.assertEqual(result, 1.0)

    def test_transmittance_decreases_with_distance(self) -> None:
        transmission_5_m = calculate_transmittance(0.1, 5.0)
        transmission_10_m = calculate_transmittance(0.1, 10.0)

        self.assertLess(transmission_10_m, transmission_5_m)

    def test_equal_optical_depth_gives_equal_transmittance(self) -> None:
        first = calculate_transmittance(0.1, 10.0)
        second = calculate_transmittance(0.2, 5.0)

        self.assertAlmostEqual(first, second)

    def test_cascaded_sections_match_combined_optical_depth(self) -> None:
        first_section = calculate_transmittance(0.1, 4.0)
        second_section = calculate_transmittance(0.2, 3.0)

        cascaded = first_section * second_section
        combined = math.exp(-((0.1 * 4.0) + (0.2 * 3.0)))

        self.assertAlmostEqual(cascaded, combined)

    def test_known_beer_lambert_result(self) -> None:
        result = calculate_transmittance(
            attenuation_per_m=0.0667,
            distance_m=10.0,
        )

        self.assertAlmostEqual(result, 0.513246, places=6)

    def test_loss_conversion(self) -> None:
        result = calculate_loss_db(0.5)

        self.assertAlmostEqual(result, 3.0103, places=4)

    def test_negative_attenuation_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_transmittance(
                attenuation_per_m=-0.1,
                distance_m=10.0,
            )

    def test_negative_distance_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_transmittance(
                attenuation_per_m=0.1,
                distance_m=-10.0,
            )

    def test_invalid_transmittance_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            calculate_loss_db(0.0)

        with self.assertRaises(ValueError):
            calculate_loss_db(1.1)

    def test_benchmark_file_is_readable(self) -> None:
        benchmark = load_benchmark()

        self.assertEqual(benchmark["dataset_id"], "EXP-001")
        self.assertEqual(benchmark["wavelength_nm"], "451")
        self.assertEqual(benchmark["medium"], "tap_water")


if __name__ == "__main__":
    unittest.main()