# Study 02 — Receiver, Noise, and Optical Link Budget

## Research Question

> How do transmitter power, beam divergence, receiver aperture,
> photodetector responsivity, background light, and electronic noise
> determine the usable range and signal-to-noise ratio of an underwater
> optical link?

## Purpose

Study 01 characterised the direct-path underwater optical channel using
absorption, molecular scattering, total beam attenuation, wavelength,
distance, uncertainty, and independent published-data benchmarking.

Study 02 connects that optical channel model to a transmitter, receiver,
photodetector, and electrical noise model.

The purpose is to calculate:

- optical power reaching the receiver;
- geometric collection efficiency;
- photodetector signal current;
- shot-noise variance;
- thermal-noise variance;
- electrical signal-to-noise ratio;
- link performance as a function of distance and wavelength.

The completed Study 02 model will provide the physical input required for
later modulation, detection, filtering, and bit-error-rate analysis.

---

## System Chain

The initial link model follows:

```text
Transmitted optical power
        ↓
Beam expansion
        ↓
Water attenuation
        ↓
Receiver-aperture collection
        ↓
Photodetector responsivity
        ↓
Signal photocurrent
        ↓
Shot noise and thermal noise
        ↓
Electrical signal-to-noise ratio