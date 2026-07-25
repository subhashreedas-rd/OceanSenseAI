# OceanSenseAI

*A research project exploring the physics and modelling of underwater optical communication channels.*

OceanSenseAI investigates the physics of light propagation in water and how underwater channel conditions influence optical communication performance.

The project combines optics, numerical modelling, signal processing, and scientific computing to develop reproducible tools for underwater optical communication research. The focus is on physically consistent models, traceable parameter sources, verification against known behaviour, and comparison with published measurements.

---

## Current Research

### Study 01 — Characterisation of Underwater Optical Transmission

**Research question**

> How do propagation distance, wavelength, absorption, and scattering influence underwater optical transmission?

The first study develops a baseline propagation model based on the Beer–Lambert attenuation law. It examines how the optical properties of water affect transmission through a homogeneous medium.

The initial model considers direct-path attenuation. Later work will investigate receiver geometry, multiple scattering, beam divergence, turbulence, and temporal dispersion.

---

## Current Progress

| Task | Status |
|---|---|
| Research framework | Complete |
| Study 01 scope and methodology | Complete |
| Core literature set selected | Complete |
| Detailed literature extraction | In progress |
| Optical-property database structure | Complete |
| Initial parameter extraction | In progress |
| Beer–Lambert propagation model | Planned |
| Model verification | Planned |
| Transmission analysis and visualisation | Planned |

---

## Research Roadmap

OceanSenseAI will progressively investigate:

1. Underwater optical propagation
2. Optical sources and photon statistics
3. Receiver and detector modelling
4. Signal and noise analysis
5. Communication performance
6. Sensitivity and uncertainty analysis
7. Benchmarking against published measurements
8. Photon-level and quantum communication models

---

## Scientific Approach

The project follows several principles:

- Physics before implementation
- Traceable parameter sources
- Verification before interpretation
- Explicit assumptions and limitations
- Reproducible computational studies
- Clear separation between simulation, benchmarking, and experimental validation

---

## Planned Repository Structure

```text
OceanSenseAI/
│
├── README.md
├── docs/
├── database/
├── src/
├── studies/
├── figures/
└── tests/
```

The repository will grow alongside the research. New files and directories will be added only when they support active or completed work.

---

## Project Status

OceanSenseAI is under active development.

The current focus is developing a traceable optical-property database and implementing the first verified baseline model of underwater optical propagation.