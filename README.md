# OceanSenseAI

*A research project exploring the physics and modelling of underwater optical communication channels.*

OceanSenseAI investigates how light propagates through water and how underwater channel conditions affect optical communication performance.

The current work focuses on physics-based channel modelling, traceable parameter selection, model verification, and comparison with published measurements. Later studies will extend the framework to optical sources, receivers, signal processing, and communication-performance analysis.

---

## Current Research

### Study 01 — Characterisation of Underwater Optical Transmission

**Research question**

> How do propagation distance, wavelength, absorption, and scattering influence underwater optical transmission?

Study 01 develops a baseline direct-path propagation model using the Beer–Lambert attenuation law.

The current implementation reads a published experimental attenuation benchmark, calculates channel transmittance and path loss, checks limiting cases, and evaluates transmission over propagation distances from 0 to 50 m.

The model currently assumes homogeneous water and does not include receiver geometry, beam divergence, multiple scattering, turbulence, temporal dispersion, or alignment errors.

Detailed assumptions, equations, verification requirements, and limitations are documented in [`docs/STUDY_01.md`](docs/STUDY_01.md).

---

## Current Progress

| Task | Status |
|---|---|
| Study 01 scope and methodology | Complete |
| Core literature set selected | Complete |
| Experimental attenuation benchmark added | Complete |
| Beer–Lambert propagation model | Complete |
| Basic verification checks | Complete |
| Distance-sweep analysis | Complete |
| Results dataset and transmission figure | Complete |
| Additional parameter extraction | In progress |
| Comparison across water conditions | Planned |
| Published-data benchmarking | Planned |

---

## Current Result

Using the published experimental attenuation coefficient of \(0.0667\ \mathrm{m^{-1}}\) at 451 nm, the baseline model predicts that direct-path transmittance decreases from 1 at zero distance to approximately 0.036 at 50 m.

![Direct-path transmittance versus propagation distance](figures/study_01/transmittance_vs_distance.png)

This result represents a single measured water condition and should not be interpreted as a general model for all underwater environments.

---

## Research Direction

Planned development includes:

1. comparison of attenuation across different water conditions;
2. wavelength-dependent absorption and scattering;
3. optical source modelling;
4. receiver and detector modelling;
5. signal and noise analysis;
6. bit-error-rate evaluation;
7. sensitivity and uncertainty analysis;
8. comparison with additional published measurements.

---

## Scientific Approach

- Use physical reasoning before adding software complexity.
- Record the origin and permitted use of model parameters.
- Verify numerical models before interpreting their outputs.
- State assumptions and limitations explicitly.
- Keep simulation, published-data benchmarking, and experimental validation distinct.
- Add new features only when they support a defined research question.

---

## Repository Structure

```text
OceanSenseAI/
├── database/
│   └── experimental_benchmarks/
├── docs/
├── figures/
│   └── study_01/
├── src/
├── studies/
│   └── study_01/
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Running Study 01

Install the required Python package:

```bash
python -m pip install -r requirements.txt
```

Run the distance-sweep study from the repository root:

```bash
python -m studies.study_01.run_distance_sweep
```

The script generates:

```text
studies/study_01/results/distance_sweep.csv
figures/study_01/transmittance_vs_distance.png
```

The core propagation calculation can also be run directly:

```bash
python src/propagation.py
```

---

## Project Status

OceanSenseAI is under active development.

The present implementation is a verified Beer–Lambert baseline evaluated using one published experimental attenuation benchmark. The next step is to introduce additional sourced optical parameters and compare transmission across different underwater conditions.