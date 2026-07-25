# Study 01 — Characterisation of Underwater Optical Transmission

## Research Question

> How do propagation distance, wavelength, absorption, and scattering influence underwater optical transmission?

## Purpose

Before modelling receivers, noise, or bit errors, the optical channel itself must be understood.

This study develops a baseline model relating the optical properties of water to channel transmittance and received optical power.

---

## Model Scope

The first version considers direct-path attenuation through homogeneous water.

It includes:

- wavelength-dependent absorption;
- wavelength-dependent scattering;
- beam attenuation;
- propagation distance;
- channel transmittance;
- received optical power.

It does not yet include:

- receiver aperture or field of view;
- beam divergence;
- multiple scattering;
- turbulence;
- temporal dispersion;
- alignment errors;
- polarisation effects;
- time-dependent water conditions.

The model is therefore a first-order description rather than a complete underwater optical channel model.

---

## Notation

| Symbol | Meaning | Unit |
|---|---|---|
| \(L\) | Propagation distance | m |
| \(\lambda\) | Optical wavelength | nm or m |
| \(a(\lambda)\) | Absorption coefficient | \(\mathrm{m^{-1}}\) |
| \(b(\lambda)\) | Scattering coefficient | \(\mathrm{m^{-1}}\) |
| \(c(\lambda)\) | Beam attenuation coefficient | \(\mathrm{m^{-1}}\) |
| \(P_t\) | Transmitted optical power | W |
| \(P_r\) | Received direct-path optical power | W |
| \(T\) | Channel transmittance | Dimensionless |

---

## Physical Background

### Absorption

Absorption removes optical energy from the propagating light field.

The wavelength-dependent absorption coefficient is written as:

$$
a(\lambda)
$$

### Scattering

Scattering changes the direction of light propagation.

A scattered photon is not necessarily destroyed, but it may leave the direct optical path and fail to reach the receiver.

The wavelength-dependent scattering coefficient is written as:

$$
b(\lambda)
$$

### Beam Attenuation

For a homogeneous medium, the beam attenuation coefficient is:

$$
c(\lambda)=a(\lambda)+b(\lambda)
$$

Absorption and scattering describe different physical processes, but both reduce the optical power remaining in the direct beam.

---

## Adopted Model

The Beer–Lambert relationship is used as the baseline propagation model:

$$
P_r(L,\lambda)=P_t(\lambda)e^{-c(\lambda)L}
$$

Channel transmittance is defined as:

$$
T(L,\lambda)=\frac{P_r}{P_t}
$$

Therefore:

$$
T(L,\lambda)=e^{-c(\lambda)L}
$$

The exponent must be dimensionless:

$$
[\mathrm{m^{-1}}][\mathrm{m}]=1
$$

---

## Derivation

The model assumes that the rate of optical power loss is proportional to the optical power remaining in the beam:

$$
\frac{dP}{dL}=-cP
$$

Separating the variables gives:

$$
\frac{dP}{P}=-c\,dL
$$

For a constant attenuation coefficient:

$$
\ln\left(\frac{P_r}{P_t}\right)=-cL
$$

Therefore:

$$
P_r=P_t e^{-cL}
$$

and:

$$
T=e^{-cL}
$$

This derivation assumes that \(c\) remains constant along the propagation path.

---

## Optical Depth

Optical depth is defined as:

$$
\tau=cL
$$

The transmittance can therefore be written as:

$$
T=e^{-\tau}
$$

Two channels with the same optical depth have the same Beer–Lambert transmittance, even if their distances and attenuation coefficients are different.

---

## Characteristic Distances

### Attenuation Length

When:

$$
L=\frac{1}{c}
$$

the transmittance becomes:

$$
T=e^{-1}\approx0.368
$$

The attenuation length is:

$$
L_e=\frac{1}{c}
$$

### Half-Power Distance

For:

$$
T=0.5
$$

the corresponding distance is:

$$
L_{1/2}=\frac{\ln 2}{c}
$$

---

## Optical Loss in Decibels

Path loss in decibels is:

$$
\mathrm{Loss}_{dB}
=
-10\log_{10}\left(\frac{P_r}{P_t}\right)
$$

Using the Beer–Lambert relationship:

$$
\mathrm{Loss}_{dB}=4.343cL
$$

Under this model:

- transmittance decreases exponentially with distance;
- loss in decibels increases linearly with distance.

---

## Assumptions

| Assumption | Meaning |
|---|---|
| Homogeneous water | Optical properties remain constant along the path |
| Constant attenuation coefficient | \(c\) does not vary with distance |
| Monochromatic source | One wavelength is considered at a time |
| Direct line of sight | Transmitter and receiver are aligned |
| No turbulence | Refractive-index fluctuations are neglected |
| No beam divergence | Geometric spreading is excluded |
| No receiver geometry | Aperture and field of view are not modelled |
| Steady channel | Optical properties do not vary with time |

---

## Parameter Provenance

Optical coefficients are not universal constants.

Reported values may depend on:

- wavelength;
- temperature;
- salinity;
- dissolved substances;
- suspended particles;
- biological material;
- measurement method;
- sample preparation;
- environmental conditions.

Every parameter used in OceanSenseAI must record:

- physical quantity;
- numerical value and unit;
- wavelength;
- medium;
- measurement conditions;
- reported uncertainty;
- measurement or derivation method;
- source reference;
- permitted model use.

Measured, derived, fitted, and reproduced values will be stored separately.

---

## Verification Requirements

The Python implementation must satisfy the following checks before its results are interpreted.

### Zero Distance

For \(L=0\):

$$
T=1
$$

### Zero Attenuation

For \(c=0\):

$$
T=1
$$

for every distance.

### Positive Attenuation

For \(c>0\), transmittance must decrease as distance increases.

### Large Distance

As \(L\rightarrow\infty\):

$$
T\rightarrow0
$$

without becoming negative.

### Physical Range

For non-negative distance and attenuation:

$$
0<T\leq1
$$

### Equal Optical Depth

If:

$$
c_1L_1=c_2L_2
$$

then:

$$
T_1=T_2
$$

### Cascaded Channel Sections

For two homogeneous sections:

$$
T_{\mathrm{total}}
=
e^{-c_1L_1}e^{-c_2L_2}
$$

which is equivalent to:

$$
T_{\mathrm{total}}
=
e^{-(c_1L_1+c_2L_2)}
$$

---

## Planned Outputs

The first implementation will generate:

1. transmittance versus propagation distance;
2. received optical power versus propagation distance;
3. path loss versus propagation distance;
4. a transmission map showing the combined effects of distance and attenuation.

All parameters used in the analysis must be linked to traceable sources.

---

## Limitations

The Beer–Lambert model treats scattering as loss from the direct beam.

It does not track light that is scattered and later enters the receiver. It therefore cannot represent:

- receiver-aperture effects;
- receiver field-of-view effects;
- multipath propagation;
- temporal pulse broadening;
- scattering-angle distributions;
- turbulence-induced fading;
- time-dependent channel behaviour.

The results must be interpreted as first-order direct-path predictions.

---

## Current Status

| Task | Status |
|---|---|
| Research question | Complete |
| Model scope | Complete |
| Mathematical formulation | Complete |
| Verification requirements | Complete |
| Parameter extraction | In progress |
| Python implementation | Planned |
| Results | Planned |
| Published-data benchmarking | Planned |

---

## Next Step

Complete the initial optical-property dataset and implement the Beer–Lambert transmittance model in Python.