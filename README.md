# OceanSenseAI

[![Tests](https://github.com/subhashreedas-rd/OceanSenseAI/actions/workflows/tests.yml/badge.svg)](https://github.com/subhashreedas-rd/OceanSenseAI/actions/workflows/tests.yml)

A physics-based modelling and signal-processing project for underwater
optical communication.

OceanSenseAI connects published optical-property data to a traceable
simulation chain covering:

- underwater optical attenuation;
- wavelength-dependent absorption and molecular scattering;
- received optical power;
- photodetector current;
- shot and thermal noise;
- on–off keying;
- waveform sampling and filtering;
- threshold detection;
- bit-error-rate analysis;
- receiver-bandwidth limitation and intersymbol interference.

The project is organised as a sequence of verified studies. Physical
channel modelling is completed before receiver and signal-processing
effects are introduced.

---

## Research Objective

The overall objective is to determine how underwater optical-channel,
transmitter, receiver, and signal-processing parameters influence
communication performance.

The implemented modelling chain is:

```text
Published optical-property data
        ↓
Absorption and molecular scattering
        ↓
Water attenuation coefficient
        ↓
Beam expansion and geometric collection
        ↓
Received optical power
        ↓
Photodetector current
        ↓
Shot noise and thermal noise
        ↓
OOK waveform generation
        ↓
Receiver filtering and decision sampling
        ↓
Recovered bits and bit-error rate