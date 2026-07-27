"""Analyse pure-water transmission across wavelength and distance."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_CSV_PATH = (
    ROOT_DIR
    / "studies"
    / "study_01"
    / "results"
    / "pure_water_total_attenuation_spectrum.csv"
)

RESULTS_DIR = ROOT_DIR / "studies" / "study_01" / "results"
FIGURES_DIR = ROOT_DIR / "figures" / "study_01"

MAP_CSV_PATH = (
    RESULTS_DIR
    / "pure_water_wavelength_distance_transmission.csv"
)

BEST_WAVELENGTH_CSV_PATH = (
    RESULTS_DIR
    / "pure_water_best_wavelength_by_distance.csv"
)

FIGURE_PATH = (
    FIGURES_DIR
    / "pure_water_wavelength_distance_transmission_map.png"
)

MIN_WAVELENGTH_NM = 350
MAX_WAVELENGTH_NM = 550
WAVELENGTH_STEP_NM = 2

MIN_DISTANCE_M = 0
MAX_DISTANCE_M = 200
DISTANCE_STEP_M = 2


def load_attenuation_spectrum() -> list[dict[str, float]]:
    """Load and validate the combined attenuation spectrum."""

    required_columns = {
        "wavelength_nm",
        "absorption_per_m",
        "molecular_scattering_per_m",
        "attenuation_per_m",
    }

    with INPUT_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(
                "Attenuation CSV does not contain a header"
            )

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(
                f"Attenuation CSV is missing columns: {missing}"
            )

        rows: list[dict[str, float]] = []

        for source_row in reader:
            wavelength_nm = float(source_row["wavelength_nm"])

            if not (
                MIN_WAVELENGTH_NM
                <= wavelength_nm
                <= MAX_WAVELENGTH_NM
            ):
                continue

            absorption = float(source_row["absorption_per_m"])

            scattering = float(
                source_row["molecular_scattering_per_m"]
            )

            attenuation = float(
                source_row["attenuation_per_m"]
            )

            if absorption < 0.0:
                raise ValueError(
                    "Absorption coefficients must be non-negative"
                )

            if scattering < 0.0:
                raise ValueError(
                    "Scattering coefficients must be non-negative"
                )

            if attenuation <= 0.0:
                raise ValueError(
                    "Attenuation coefficients must be positive"
                )

            expected_attenuation = absorption + scattering

            if not math.isclose(
                attenuation,
                expected_attenuation,
                rel_tol=1.0e-10,
                abs_tol=1.0e-12,
            ):
                raise ValueError(
                    "Attenuation coefficient does not equal "
                    "absorption plus scattering"
                )

            rows.append(
                {
                    "wavelength_nm": wavelength_nm,
                    "absorption_per_m": absorption,
                    "scattering_per_m": scattering,
                    "attenuation_per_m": attenuation,
                }
            )

    rows.sort(
        key=lambda row: row["wavelength_nm"]
    )

    expected_wavelengths = [
        float(wavelength)
        for wavelength in range(
            MIN_WAVELENGTH_NM,
            MAX_WAVELENGTH_NM + 1,
            WAVELENGTH_STEP_NM,
        )
    ]

    actual_wavelengths = [
        row["wavelength_nm"]
        for row in rows
    ]

    if actual_wavelengths != expected_wavelengths:
        raise ValueError(
            "Attenuation wavelengths do not match the expected "
            "350–550 nm grid at 2 nm intervals"
        )

    return rows


def calculate_transmission_map(
    attenuation_rows: list[dict[str, float]],
) -> tuple[
    list[dict[str, float]],
    list[dict[str, float]],
    list[list[float]],
]:
    """Calculate transmittance and path loss across the domain."""

    map_rows: list[dict[str, float]] = []
    best_rows: list[dict[str, float]] = []
    transmittance_grid: list[list[float]] = []

    minimum_attenuation_row = min(
        attenuation_rows,
        key=lambda row: row["attenuation_per_m"],
    )

    for distance_m in range(
        MIN_DISTANCE_M,
        MAX_DISTANCE_M + 1,
        DISTANCE_STEP_M,
    ):
        distance = float(distance_m)
        grid_row: list[float] = []

        for coefficient_row in attenuation_rows:
            wavelength_nm = coefficient_row["wavelength_nm"]
            attenuation = coefficient_row["attenuation_per_m"]

            optical_depth = attenuation * distance

            transmittance = math.exp(-optical_depth)

            path_loss_db = (
                10.0
                / math.log(10.0)
                * optical_depth
            )

            grid_row.append(transmittance)

            map_rows.append(
                {
                    "distance_m": distance,
                    "wavelength_nm": wavelength_nm,
                    "attenuation_per_m": attenuation,
                    "optical_depth": optical_depth,
                    "transmittance": transmittance,
                    "path_loss_db": path_loss_db,
                }
            )

        transmittance_grid.append(grid_row)

        best_attenuation = minimum_attenuation_row[
            "attenuation_per_m"
        ]

        best_transmittance = math.exp(
            -best_attenuation * distance
        )

        best_path_loss_db = (
            10.0
            / math.log(10.0)
            * best_attenuation
            * distance
        )

        best_rows.append(
            {
                "distance_m": distance,
                "best_wavelength_nm": (
                    minimum_attenuation_row["wavelength_nm"]
                ),
                "minimum_attenuation_per_m": best_attenuation,
                "maximum_transmittance": best_transmittance,
                "minimum_path_loss_db": best_path_loss_db,
            }
        )

    return map_rows, best_rows, transmittance_grid


def write_map_csv(
    rows: list[dict[str, float]],
) -> None:
    """Write the complete wavelength–distance results."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "distance_m",
        "wavelength_nm",
        "attenuation_per_m",
        "optical_depth",
        "transmittance",
        "path_loss_db",
    ]

    with MAP_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "distance_m": (
                        f"{row['distance_m']:.1f}"
                    ),
                    "wavelength_nm": (
                        f"{row['wavelength_nm']:.1f}"
                    ),
                    "attenuation_per_m": (
                        f"{row['attenuation_per_m']:.12e}"
                    ),
                    "optical_depth": (
                        f"{row['optical_depth']:.12e}"
                    ),
                    "transmittance": (
                        f"{row['transmittance']:.12e}"
                    ),
                    "path_loss_db": (
                        f"{row['path_loss_db']:.9f}"
                    ),
                }
            )


def write_best_wavelength_csv(
    rows: list[dict[str, float]],
) -> None:
    """Write the highest-transmittance wavelength by distance."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "distance_m",
        "best_wavelength_nm",
        "minimum_attenuation_per_m",
        "maximum_transmittance",
        "minimum_path_loss_db",
    ]

    with BEST_WAVELENGTH_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "distance_m": (
                        f"{row['distance_m']:.1f}"
                    ),
                    "best_wavelength_nm": (
                        f"{row['best_wavelength_nm']:.1f}"
                    ),
                    "minimum_attenuation_per_m": (
                        f"{row['minimum_attenuation_per_m']:.12e}"
                    ),
                    "maximum_transmittance": (
                        f"{row['maximum_transmittance']:.12e}"
                    ),
                    "minimum_path_loss_db": (
                        f"{row['minimum_path_loss_db']:.9f}"
                    ),
                }
            )


def create_transmission_map(
    attenuation_rows: list[dict[str, float]],
    transmittance_grid: list[list[float]],
) -> None:
    """Create the wavelength–distance transmission map."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    minimum_transmittance = min(
        value
        for grid_row in transmittance_grid
        for value in grid_row
        if value > 0.0
    )

    best_row = min(
        attenuation_rows,
        key=lambda row: row["attenuation_per_m"],
    )

    figure, axis = plt.subplots(figsize=(9.0, 6.0))

    image = axis.imshow(
        transmittance_grid,
        origin="lower",
        aspect="auto",
        extent=[
            MIN_WAVELENGTH_NM,
            MAX_WAVELENGTH_NM,
            MIN_DISTANCE_M,
            MAX_DISTANCE_M,
        ],
        norm=LogNorm(
            vmin=minimum_transmittance,
            vmax=1.0,
        ),
    )

    axis.axvline(
        best_row["wavelength_nm"],
        linestyle="--",
        linewidth=1.5,
        label=(
            "Minimum attenuation: "
            f"{best_row['wavelength_nm']:.0f} nm"
        ),
    )

    axis.set_xlabel("Wavelength (nm)")
    axis.set_ylabel("Propagation distance (m)")

    axis.set_title(
        "Pure-water direct-path transmission map\n"
        "Combined measured absorption and modelled "
        "molecular scattering"
    )

    axis.legend()

    colour_bar = figure.colorbar(
        image,
        ax=axis,
    )

    colour_bar.set_label(
        "Direct-path transmittance"
    )

    figure.tight_layout()

    figure.savefig(
        FIGURE_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_summary(
    attenuation_rows: list[dict[str, float]],
    best_rows: list[dict[str, float]],
) -> None:
    """Print key wavelength–distance results."""

    best_attenuation_row = min(
        attenuation_rows,
        key=lambda row: row["attenuation_per_m"],
    )

    print()
    print("Pure-water wavelength–distance transmission")
    print("-------------------------------------------")

    print(
        f"Number of wavelengths: "
        f"{len(attenuation_rows)}"
    )

    print(
        "Wavelength range: "
        f"{attenuation_rows[0]['wavelength_nm']:.0f}–"
        f"{attenuation_rows[-1]['wavelength_nm']:.0f} nm"
    )

    print(
        f"Number of distances: "
        f"{len(best_rows)}"
    )

    print(
        "Distance range: "
        f"{best_rows[0]['distance_m']:.0f}–"
        f"{best_rows[-1]['distance_m']:.0f} m"
    )

    print()
    print(
        "Minimum-attenuation wavelength: "
        f"{best_attenuation_row['wavelength_nm']:.0f} nm"
    )

    print(
        "Minimum attenuation coefficient: "
        f"{best_attenuation_row['attenuation_per_m']:.6e} m^-1"
    )

    print()
    print(
        f"{'Distance':>10} "
        f"{'Best wavelength':>18} "
        f"{'Transmittance':>16} "
        f"{'Path loss':>14}"
    )

    print("-" * 64)

    summary_distances = {
        10.0,
        50.0,
        100.0,
        200.0,
    }

    for row in best_rows:
        if row["distance_m"] not in summary_distances:
            continue

        print(
            f"{row['distance_m']:>8.0f} m "
            f"{row['best_wavelength_nm']:>15.0f} nm "
            f"{row['maximum_transmittance']:>16.6f} "
            f"{row['minimum_path_loss_db']:>11.3f} dB"
        )

    print()
    print(
        "Under the present homogeneous Beer–Lambert model, "
        "the minimum-attenuation wavelength remains the "
        "highest-transmittance wavelength at every positive "
        "distance."
    )

    print()
    print(f"Saved map data: {MAP_CSV_PATH}")

    print(
        "Saved best-wavelength data: "
        f"{BEST_WAVELENGTH_CSV_PATH}"
    )

    print(f"Saved figure: {FIGURE_PATH}")


def main() -> None:
    """Run the wavelength–distance transmission analysis."""

    attenuation_rows = load_attenuation_spectrum()

    (
        map_rows,
        best_rows,
        transmittance_grid,
    ) = calculate_transmission_map(
        attenuation_rows
    )

    write_map_csv(map_rows)
    write_best_wavelength_csv(best_rows)

    create_transmission_map(
        attenuation_rows,
        transmittance_grid,
    )

    print_summary(
        attenuation_rows,
        best_rows,
    )


if __name__ == "__main__":
    main()