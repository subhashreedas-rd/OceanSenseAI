from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "database"
    / "optical_properties"
    / "absorption"
    / "pure_water"
    / "mason_cone_fry_2016_pure_water_absorption.csv"
)

FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "study_01"
    / "pure_water_absorption_spectrum.png"
)


def load_absorption_data(
    path: Path = DATA_PATH,
) -> list[dict[str, str]]:
    """Load the validated pure-water absorption dataset."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))

    if not records:
        raise ValueError("The absorption dataset contains no records.")

    return records


def create_figure(
    records: list[dict[str, str]],
) -> tuple[Path, int, float]:
    """Plot absorption coefficient and reported uncertainty."""

    parsed_records = sorted(
        records,
        key=lambda record: int(record["wavelength_nm"]),
    )

    wavelengths = [
        int(record["wavelength_nm"])
        for record in parsed_records
    ]

    absorption_values = [
        float(record["absorption_per_m"])
        for record in parsed_records
    ]

    uncertainties = [
        float(record["uncertainty_per_m"])
        for record in parsed_records
    ]

    lower_bounds = [
        max(value - uncertainty, 1e-12)
        for value, uncertainty in zip(
            absorption_values,
            uncertainties,
        )
    ]

    upper_bounds = [
        value + uncertainty
        for value, uncertainty in zip(
            absorption_values,
            uncertainties,
        )
    ]

    minimum_index = absorption_values.index(
        min(absorption_values)
    )

    minimum_wavelength = wavelengths[minimum_index]
    minimum_absorption = absorption_values[minimum_index]

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7.5, 4.8))

    plt.plot(
        wavelengths,
        absorption_values,
        linewidth=2,
        label="Measured absorption",
    )

    plt.fill_between(
        wavelengths,
        lower_bounds,
        upper_bounds,
        alpha=0.25,
        label="Reported uncertainty",
    )

    plt.scatter(
        [minimum_wavelength],
        [minimum_absorption],
        zorder=3,
    )

    plt.annotate(
        (
            f"Minimum: {minimum_wavelength} nm\n"
            f"a = {minimum_absorption:.6f} m⁻¹"
        ),
        xy=(minimum_wavelength, minimum_absorption),
        xytext=(35, 25),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )

    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Absorption coefficient, a (m⁻¹)")
    plt.title("Pure-water absorption spectrum")
    plt.xlim(250, 550)
    plt.yscale("log")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=300)
    plt.close()

    return (
        FIGURE_PATH,
        minimum_wavelength,
        minimum_absorption,
    )


def main() -> None:
    records = load_absorption_data()

    (
        figure_path,
        minimum_wavelength,
        minimum_absorption,
    ) = create_figure(records)

    print("Pure-water absorption analysis")
    print("Source: Mason, Cone and Fry (2016)")
    print(f"Rows: {len(records)}")
    print(
        f"Minimum: {minimum_wavelength} nm, "
        f"{minimum_absorption:.6f} m^-1"
    )
    print(f"Figure saved to: {figure_path}")
    print("Interpretation scope: absorption only")


if __name__ == "__main__":
    main()