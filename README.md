# OceanSenseAI

[![Tests](https://github.com/subhashreedas-rd/OceanSenseAI/actions/workflows/tests.yml/badge.svg)](https://github.com/subhashreedas-rd/OceanSenseAI/actions/workflows/tests.yml)

**OceanSenseAI investigates how physical processes within underwater optical channels ultimately influence received signals and communication performance.**

## Why This Project?

Underwater optical communication cannot be understood by examining the water channel, receiver, and signal processing independently.

Absorption and scattering determine how much optical power survives propagation. Beam expansion determines how much of that light enters the receiver. Detector and electronic noise affect whether transmitted symbols can be distinguished, while limited receiver bandwidth can distort one pulse into the next.

OceanSenseAI develops these mechanisms progressively through traceable, physics-based studies. The aim is not only to generate numerical results, but to understand which physical assumptions produce those results, how they can be verified, and how reliably they should be interpreted.

## Current Research

### Study 01 — Underwater Optical-Channel Modelling

**Research question**

How do wavelength-dependent absorption and molecular scattering determine direct-path optical transmission through water?

**Study focus**

- published pure-water optical-property data;
- wavelength-dependent molecular scattering;
- total beam attenuation;
- Beer–Lambert propagation;
- uncertainty propagation;
- sensitivity to dataset selection;
- benchmarking against selected published measurements.

**Main finding**

The study shows that predicted underwater optical transmission depends strongly on the optical-property dataset used. Comparison with independent data demonstrates that an apparently favourable wavelength region is not universal, but depends on the underlying parameter source and modelling assumptions.

[Read Study 01](docs/STUDY_01.md)

---

### Study 02 — Link and Signal-Recovery Modelling

**Research question**

How do propagation loss, geometric collection, receiver noise, digital detection, and receiver bandwidth jointly influence underwater communication performance?

**Study focus**

- beam divergence and receiver-aperture collection;
- received optical power and detector responsivity;
- shot noise and thermal noise;
- on–off keying and threshold detection;
- theoretical and Monte Carlo bit-error-rate analysis;
- sampled waveforms and integrate-and-dump detection;
- receiver-bandwidth limitation;
- intersymbol interference and eye closure.

**Main finding**

The study establishes a traceable connection between optical propagation and recovered digital bits. Analytical and numerical bit-error-rate results agree under the baseline assumptions, while bandwidth limitation demonstrates how pulse memory and intersymbol interference can degrade detection even when the optical link itself remains unchanged.

[Read Study 02](docs/STUDY_02.md)

---

### Study 03A — Photon-Budget Modelling

**Research question**

How do received optical power, wavelength, bit duration, and detector efficiency determine the mean number of photons available during each transmitted bit?

**Study focus**

- photon energy as a function of wavelength;
- optical energy received during one bit;
- mean photons reaching the detector;
- detector efficiency inferred from responsivity;
- mean detected photons per bit;
- photon-budget variation with propagation distance.

**Main finding**

The study connects the existing continuous-power link model to a photon-level energy description. Under the present transmitter and bit-rate assumptions, the simulated link remains in a many-photon regime throughout the investigated distance range. A separate statistical counting model is therefore required before individual detection events can be analysed.

[Read Study 03A](docs/STUDY_03.md)

## Current Progress

| Research component | Status |
|---|---|
| Optical-property data and provenance | Implemented and documented |
| Pure-water absorption and scattering model | Implemented and verified |
| Selected published-data benchmarking | Completed for the baseline |
| Optical link-budget model | Implemented and verified |
| Photon-budget model | Implemented and verified |
| Receiver-noise model | Implemented and verified |
| OOK theoretical BER | Implemented and verified |
| Monte Carlo BER simulation | Implemented and verified |
| Sampled waveform detection | Implemented and verified |
| Receiver bandwidth and ISI study | Completed for the baseline |
| Automated testing | Active |
| End-to-end experimental validation | Future work |

## Scientific Principles

- **Physics before implementation** — each model begins with a defined physical mechanism and mathematical formulation.
- **Traceable parameters** — published values, engineering assumptions, units, and environmental conditions are documented.
- **Verification before interpretation** — implementations are checked using analytical results, limiting cases, unit tests, and selected independent data.
- **Explicit assumptions** — simplifications are stated rather than hidden.
- **Reproducibility** — controlled parameters, automated tests, and fixed random seeds reproduce the reported simulations.

## Research Workflow

```text
Scientific question
        ↓
Physical model
        ↓
Parameter selection and provenance
        ↓
Mathematical formulation
        ↓
Numerical implementation
        ↓
Verification and benchmarking
        ↓
Simulation
        ↓
Scientific interpretation
        ↓
Limitations and next questions
```

The software is treated as a research instrument. The scientific value lies in the formulation, verification, and interpretation of the models.

## Current Findings

- Optical-property dataset selection can substantially influence predicted attenuation behaviour.
- Water attenuation and geometric collection loss affect received power through different physical mechanisms and must be modelled separately.
- Monte Carlo detection results reproduce the corresponding analytical behaviour under the baseline noise assumptions.
- Oversampling improves waveform representation without automatically improving the underlying decision SNR.
- Limited receiver bandwidth introduces pulse memory, reduces eye opening, and increases bit errors through intersymbol interference.
- The current transmitter and bit-rate assumptions produce a many-photon link, providing a foundation for future discrete photon-counting studies.

Detailed numerical results, figures, equations, uncertainty analyses, and verification cases are provided in the individual study documents.

## Scope and Limitations

OceanSenseAI is currently a controlled simulation framework rather than a complete model of a deployed underwater communication system.

The present studies use homogeneous and stationary water properties, direct-path attenuation, ideal alignment, simplified beam geometry, fixed system parameters, Gaussian receiver-noise models, uncoded binary signalling, simplified receiver electronics, and mean-value photon-budget calculations.

Time-varying water conditions, platform motion, pointing instability, detailed multiple-scattering delays, complete detector and amplifier circuitry, synchronization errors, channel coding, discrete photon-count statistics, and end-to-end experimental validation remain outside the current scope.

Reported link, communication, and photon-budget results therefore describe behaviour under explicit baseline assumptions. They should not be interpreted as guaranteed operating performance for physical hardware.

## Future Development

Future studies may progressively increase the physical realism of the framework through discrete photon-counting models, time-varying channel models, pointing and platform effects, more detailed receiver modelling, advanced detection methods, and comparison with experimental measurements.

New extensions will be introduced only when the existing physical assumptions and numerical implementations have been sufficiently verified.

## Explore the Repository

- [`docs/STUDY_01.md`](docs/STUDY_01.md) — optical-channel formulation, parameter sources, verification, uncertainty, and interpretation.
- [`docs/STUDY_02.md`](docs/STUDY_02.md) — link budget, receiver noise, OOK detection, Monte Carlo analysis, waveforms, and ISI.
- [`docs/STUDY_03.md`](docs/STUDY_03.md) — photon energy, photons per bit, responsivity-derived efficiency, verification, and interpretation.
- [`src/`](src/) — physical and signal-processing models.
- [`studies/`](studies/) — reproducible study scripts.
- [`tests/`](tests/) — automated numerical verification.
- [`database/`](database/) — source parameters and generated results.
- [`figures/`](figures/) — generated scientific figures.

## Reproducing the Studies

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the automated tests:

```bash
python -m unittest discover -s tests
```

Individual study scripts are located in:

```text
studies/study_01/
studies/study_02/
studies/study_03/
```