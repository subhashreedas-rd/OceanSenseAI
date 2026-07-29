# Study 01 — Characterisation of Underwater Optical Transmission

## Research Question

> How do propagation distance, wavelength, absorption, and scattering influence underwater optical transmission?

## Purpose

Before modelling receivers, noise, or bit errors, the optical channel itself must be understood.

This study develops a baseline model relating the optical properties of water to channel transmittance and received direct-path optical power.

---

## Model Scope

The present model considers direct-path attenuation through homogeneous water.

It includes:

- wavelength-dependent absorption;
- wavelength-dependent molecular scattering;
- beam attenuation;
- propagation distance;
- channel transmittance;
- received direct-path optical power.

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
| \(\tau\) | Optical depth | Dimensionless |
| \(\beta(90,\lambda,T)\) | Volume scattering function at \(90^\circ\) | \(\mathrm{m^{-1}\,sr^{-1}}\) |
| \(\delta\) | Molecular depolarisation ratio | Dimensionless |

---

## Physical Background

### Absorption

Absorption removes optical energy from the propagating light field.

The wavelength-dependent absorption coefficient is written as:

$$
a(\lambda).
$$

### Scattering

Scattering changes the direction of light propagation.

A scattered photon is not necessarily destroyed, but it may leave the direct optical path and fail to reach the receiver.

The wavelength-dependent scattering coefficient is written as:

$$
b(\lambda).
$$

### Beam Attenuation

For a homogeneous medium, the beam attenuation coefficient is:

$$
c(\lambda)=a(\lambda)+b(\lambda).
$$

Absorption and scattering describe different physical processes, but both reduce the optical power remaining in the direct beam.

---

## Adopted Model

The Beer–Lambert relationship is used as the baseline propagation model:

$$
P_r(L,\lambda)=P_t(\lambda)e^{-c(\lambda)L}.
$$

Channel transmittance is defined as:

$$
T(L,\lambda)=\frac{P_r}{P_t}.
$$

Therefore:

$$
T(L,\lambda)=e^{-c(\lambda)L}.
$$

The exponent must be dimensionless:

$$
[\mathrm{m^{-1}}][\mathrm{m}]=1.
$$

---

## Derivation

The model assumes that the rate of optical power loss is proportional to the optical power remaining in the direct beam:

$$
\frac{dP}{dL}=-cP.
$$

Separating the variables gives:

$$
\frac{dP}{P}=-c\,dL.
$$

For a constant attenuation coefficient:

$$
\ln\left(\frac{P_r}{P_t}\right)=-cL.
$$

Therefore:

$$
P_r=P_t e^{-cL},
$$

and:

$$
T=e^{-cL}.
$$

This derivation assumes that \(c\) remains constant along the propagation path.

---

## Optical Depth

Optical depth is defined as:

$$
\tau=cL.
$$

The transmittance can therefore be written as:

$$
T=e^{-\tau}.
$$

Two channels with the same optical depth have the same Beer–Lambert transmittance, even if their distances and attenuation coefficients are different.

---

## Characteristic Distances

### Attenuation Length

When:

$$
L=\frac{1}{c},
$$

the transmittance becomes:

$$
T=e^{-1}\approx0.368.
$$

The attenuation length is therefore:

$$
L_e=\frac{1}{c}.
$$

### Half-Power Distance

For:

$$
T=0.5,
$$

the corresponding distance is:

$$
L_{1/2}=\frac{\ln 2}{c}.
$$

---

## Optical Loss in Decibels

Path loss in decibels is:

$$
\mathrm{Loss}_{dB}
=
-10\log_{10}\left(\frac{P_r}{P_t}\right).
$$

Using the Beer–Lambert relationship:

$$
\mathrm{Loss}_{dB}=4.343cL.
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
| Scattering treated as direct-beam loss | Scattered-light recovery is not modelled |

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

Measured, derived, fitted, and reproduced values are stored separately.

---

## Verification Requirements

The Python implementation must satisfy the following checks before its results are interpreted.

### Zero Distance

For \(L=0\):

$$
T=1.
$$

### Zero Attenuation

For \(c=0\):

$$
T=1
$$

for every propagation distance.

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
0<T\leq1.
$$

### Equal Optical Depth

If:

$$
c_1L_1=c_2L_2,
$$

then:

$$
T_1=T_2.
$$

### Cascaded Channel Sections

For two homogeneous sections:

$$
T_{\mathrm{total}}
=
e^{-c_1L_1}e^{-c_2L_2},
$$

which is equivalent to:

$$
T_{\mathrm{total}}
=
e^{-(c_1L_1+c_2L_2)}.
$$

### Spectral Coefficient Consistency

For every wavelength included in the combined pure-water spectrum:

$$
c(\lambda)=a(\lambda)+b(\lambda).
$$

The absorption coefficient must not be relabelled as total attenuation unless an independently sourced or physically justified scattering coefficient has been included.

---

## Implemented Outputs

The implementation currently generates:

1. transmittance versus propagation distance;
2. received optical power versus propagation distance;
3. path loss versus propagation distance;
4. direct-path loss comparisons across literature water types;
5. a wavelength-dependent pure-water absorption spectrum;
6. a validated pure-water molecular-scattering spectrum;
7. a comparison between calculated and published volume-scattering values;
8. a combined absorption, scattering, and total attenuation spectrum;
9. machine-readable CSV files containing calculated and source-reported values;
10. automated unit tests and dataset-validation checks;
11. continuous validation through GitHub Actions.

The implementation also includes a wavelength–distance transmission map, first-order uncertainty propagation, and an independent 2025 single-wavelength attenuation benchmark.

---

## Limitations

The Beer–Lambert model treats scattering as loss from the direct beam.

It does not track light that is scattered and later enters the receiver. It therefore cannot represent:

- receiver-aperture effects;
- receiver field-of-view effects;
- multipath propagation;
- temporal pulse broadening;
- scattering-angle-dependent receiver collection;
- turbulence-induced fading;
- time-dependent channel behaviour;
- geometric beam spreading;
- transmitter–receiver misalignment.

The results must be interpreted as first-order direct-path predictions.

---

## Comparison Across Water Types

A direct-path propagation analysis was performed using four literature coefficient sets representing pure sea, clear ocean, coastal water, and turbid harbour water.

For each water type, the beam attenuation coefficient was calculated as:

$$
c=a+b.
$$

The resulting coefficients were:

| Water type | \(a\) (\(\mathrm{m^{-1}}\)) | \(b\) (\(\mathrm{m^{-1}}\)) | \(c\) (\(\mathrm{m^{-1}}\)) |
|---|---:|---:|---:|
| Pure sea | 0.0405 | 0.0025 | 0.043 |
| Clear ocean | 0.114 | 0.037 | 0.151 |
| Coastal | 0.179 | 0.219 | 0.398 |
| Turbid harbour | 0.366 | 1.824 | 2.190 |

These coefficient sets are used as literature-based simulation references rather than as measurements collected within OceanSenseAI.

Under the Beer–Lambert model, path loss increases linearly with both attenuation coefficient and propagation distance:

$$
\mathrm{Loss}_{dB}=4.343cL.
$$

The comparison shows that water condition strongly influences the practical propagation range. Pure-sea water produces the lowest direct-path loss, while the turbid-harbour coefficient set produces extremely high loss over relatively short distances.

![Direct-path loss across water types](../figures/study_01/water_type_comparison.png)

The comparison remains a first-order analysis. It does not account for receiver geometry, scattered-light recovery, turbulence, alignment, or wavelength dependence within each coefficient set.

---

## Wavelength-Dependent Pure-Water Absorption

A wavelength-dependent absorption dataset was added from the experimental measurements of Mason, Cone, and Fry (2016).

The dataset contains 131 source-reported values covering wavelengths from 250 to 550 nm.

The measurements were obtained using an integrating-cavity absorption meter designed to measure absorption independently of scattering.

The reported absorption coefficient reaches its minimum at 344 nm:

$$
a(344\ \mathrm{nm})
=
0.000810\ \mathrm{m^{-1}}.
$$

![Pure-water absorption spectrum](../figures/study_01/pure_water_absorption_spectrum.png)

The spectrum shows a decrease in absorption from the ultraviolet region towards 344 nm, followed by increasing absorption at longer wavelengths.

A logarithmic vertical scale is used because the measured values span nearly two orders of magnitude.

The shaded region represents the uncertainty reported for each measurement in the source table.

The absorption dataset represents \(a(\lambda)\) only. It does not independently represent the complete beam attenuation coefficient:

$$
c(\lambda)=a(\lambda)+b(\lambda).
$$

A wavelength-dependent scattering model was therefore implemented and validated before total spectral attenuation was calculated.

---

## Pure-Water Scattering Model

Wavelength-dependent molecular scattering by pure water was calculated using the physical model presented by Zhang and Hu (2009).

The model is based on the Einstein–Smoluchowski description of scattering caused by microscopic density fluctuations in a particle-free liquid.

The volume scattering function at a scattering angle of \(90^\circ\) is:

$$
\beta(90,\lambda,T)=
\frac{\pi^2}{2\lambda^4}
\left[
\rho
\left(
\frac{\partial n^2}{\partial \rho}
\right)_T
\right]^2
kT\beta_T f(\delta),
$$

where:

- \(\lambda\) is the wavelength in vacuum;
- \(\rho\) is the density of pure water;
- \(n\) is the refractive index of pure water;
- \(k\) is the Boltzmann constant;
- \(T\) is the absolute temperature;
- \(\beta_T\) is the isothermal compressibility;
- \(\delta\) is the molecular depolarisation ratio.

The Cabannes factor is:

$$
f(\delta)=\frac{6+6\delta}{6-7\delta}.
$$

The density derivative of the squared refractive index was calculated using the Proutiere–Morel–Hu formulation:

$$
\rho
\left(
\frac{\partial n^2}{\partial \rho}
\right)_T
=
\rho
\left(
\frac{\partial n^2}{\partial \rho}
\right)_P
=
(n^2-1)
\left[
1+
\frac{2}{3}(n^2+2)
\left(
\frac{n^2-1}{3n}
\right)^2
\right].
$$

Zhang and Hu refer to this formulation as the PMH model.

The molecular depolarisation ratio was set to:

$$
\delta=0.039,
$$

consistent with the later experimental measurements reported by Zhang et al. (2019).

Temperature was retained as an explicit model input.

The implementation also includes:

- the refractive index of standard air;
- the temperature- and wavelength-dependent refractive index of pure water;
- the isothermal compressibility of pure water;
- the PMH density derivative;
- the Cabannes correction;
- the volume scattering function at \(90^\circ\);
- the integrated molecular-scattering coefficient.

The total molecular-scattering coefficient was obtained by integrating the angular scattering function over the complete solid angle:

$$
b(\lambda,T)
=
\frac{8\pi}{3}
\frac{2+\delta}{1+\delta}
\beta(90,\lambda,T).
$$

### Scattering-Model Validation

The implementation was validated at \(20^\circ\mathrm{C}\) against five Morel measurements reported by Zhang and Hu at:

- 366 nm;
- 405 nm;
- 436 nm;
- 546 nm;
- 578 nm.

The maximum absolute relative difference between the calculated and measured volume-scattering values was:

$$
1.398\%.
$$

This was below the adopted validation limit of 2%.

![Pure-water molecular-scattering spectrum](../figures/study_01/pure_water_scattering_spectrum.png)

The scattering spectrum was calculated over 350–700 nm.

The combined absorption-and-scattering analysis was restricted to the overlapping wavelength range of 350–550 nm.

The model represents molecular scattering by pure, particle-free water. It does not include scattering by suspended particles, dissolved material, bubbles, biological material, or turbulence.

---

## Combined Pure-Water Attenuation Spectrum

The measured pure-water absorption spectrum was combined with the validated molecular-scattering model to calculate the wavelength-dependent beam attenuation coefficient:

$$
c(\lambda)=a(\lambda)+b(\lambda),
$$

where \(a(\lambda)\) is the measured absorption coefficient and \(b(\lambda)\) is the calculated molecular-scattering coefficient.

The analysis was restricted to the overlapping wavelength range of 350–550 nm.

Absorption values were taken directly from the Mason, Cone, and Fry dataset without interpolation.

Molecular scattering was evaluated at the nominal measurement temperature of:

$$
23^\circ\mathrm{C},
$$

using a depolarisation ratio of:

$$
\delta=0.039.
$$

The calculated total attenuation reached its minimum at 416 nm.

At this wavelength:

$$
a(416\ \mathrm{nm})
=
2.8800\times10^{-3}\ \mathrm{m^{-1}},
$$

$$
b(416\ \mathrm{nm})
=
4.2551\times10^{-3}\ \mathrm{m^{-1}},
$$

and therefore:

$$
c(416\ \mathrm{nm})
=
7.1351\times10^{-3}\ \mathrm{m^{-1}}.
$$

Molecular scattering contributes approximately:

$$
59.64\%
$$

of the total beam attenuation at 416 nm.

This result demonstrates that the wavelength of minimum absorption does not necessarily correspond to the wavelength of minimum total beam attenuation.

The absorption coefficient reaches its minimum at 344 nm, but molecular scattering increases strongly towards shorter wavelengths. The balance between decreasing scattering and increasing absorption shifts the calculated minimum total attenuation to 416 nm.

![Pure-water absorption, scattering, and attenuation](../figures/study_01/pure_water_absorption_scattering_attenuation.png)

The combined dataset preserves the uncertainty reported for the absorption measurements.

Uncertainty associated with the molecular-scattering model has not yet been propagated into the total attenuation coefficient.

The calculated attenuation represents direct collimated-beam loss in pure, particle-free water. It does not account for:

- scattered-light collection by the receiver;
- suspended particles;
- dissolved material;
- bubbles;
- biological material;
- turbulence;
- beam divergence;
- transmitter–receiver alignment losses.

---

## Wavelength–Distance Transmission Analysis

The combined wavelength-dependent attenuation spectrum was used to
calculate direct-path transmittance and path loss over wavelengths from
350 to 550 nm and propagation distances from 0 to 200 m.

For each wavelength and distance:

$$
T(L,\lambda)=e^{-c(\lambda)L},
$$

and:

$$
\mathrm{Loss}_{dB}(L,\lambda)
=
\frac{10}{\ln 10}c(\lambda)L.
$$

The minimum attenuation coefficient occurs at 416 nm:

$$
c(416\ \mathrm{nm})
=
7.1351\times10^{-3}\ \mathrm{m^{-1}}.
$$

Under the present homogeneous Beer–Lambert model, this wavelength
provides the highest direct-path transmittance at every positive
propagation distance.

Representative results at 416 nm are:

| Distance | Transmittance | Path loss |
|---:|---:|---:|
| 10 m | 0.9311 | 0.310 dB |
| 50 m | 0.6999 | 1.549 dB |
| 100 m | 0.4899 | 3.099 dB |
| 200 m | 0.2400 | 6.197 dB |

![Pure-water wavelength–distance transmission map](../figures/study_01/pure_water_wavelength_distance_transmission_map.png)

The map shows how the direct-path transmission window narrows as
propagation distance increases. Wavelengths with larger attenuation
coefficients lose power more rapidly, while the region around 416 nm
retains the highest transmittance.

The optimum wavelength does not change with distance in this model
because the attenuation spectrum is assumed to remain constant along
the propagation path. For every positive distance, maximising

$$
e^{-c(\lambda)L}
$$

is equivalent to minimising \(c(\lambda)\).

This conclusion applies only to the present direct-path model. The
preferred operating wavelength may change when source power, detector
responsivity, receiver geometry, background light, turbulence,
alignment, or scattered-light collection are included.

## Combined Uncertainty Analysis

A first-order uncertainty analysis was performed for the combined
pure-water attenuation and transmission predictions.

The absorption uncertainty was taken directly from the source-reported
values in the Mason, Cone, and Fry dataset. The molecular-scattering
coefficient was assigned an initial relative uncertainty of:

$$
\frac{u_b}{b}=2\%.
$$

This value is an explicit modelling assumption based on the adopted
scattering-model validation criterion. It is not a source-reported
measurement uncertainty.

Assuming that the absorption and scattering uncertainties are
independent, the combined attenuation uncertainty was calculated as:

$$
u_c(\lambda)
=
\sqrt{
u_a^2(\lambda)
+
u_b^2(\lambda)
}.
$$

At the nominal minimum-attenuation wavelength of 416 nm:

$$
c(416\ \mathrm{nm})
=
7.1351\times10^{-3}\ \mathrm{m^{-1}},
$$

and the estimated combined uncertainty is:

$$
u_c(416\ \mathrm{nm})
=
3.1184\times10^{-4}\ \mathrm{m^{-1}}.
$$

The corresponding relative attenuation uncertainty is approximately:

$$
4.37\%.
$$

The attenuation length is:

$$
L_e
=
140.153\pm6.125\ \mathrm{m},
$$

while the half-power distance is:

$$
L_{1/2}
=
97.146\pm4.246\ \mathrm{m}.
$$

For direct-path transmittance,

$$
T(L,\lambda)=e^{-c(\lambda)L},
$$

the first-order propagated uncertainty was calculated using:

$$
\frac{\partial T}{\partial c}
=
-LT,
$$

giving:

$$
u_T(L,\lambda)
=
L\,T(L,\lambda)\,u_c(\lambda).
$$

At 416 nm and a propagation distance of 100 m:

$$
T
=
0.489922\pm0.015278,
$$

and the direct-path loss is:

$$
\mathrm{Loss}_{dB}
=
3.099\pm0.135\ \mathrm{dB}.
$$

![Pure-water attenuation uncertainty](../figures/study_01/pure_water_attenuation_uncertainty.png)

![Pure-water transmittance uncertainty at 416 nm](../figures/study_01/pure_water_transmittance_uncertainty_416nm.png)

The uncertainty bounds increase in their practical importance as
propagation distance increases because small uncertainty in the
attenuation coefficient is amplified through the exponential
transmission relationship.

The present analysis must be interpreted as an initial uncertainty
estimate. The absorption contribution is based on source-reported
measurement uncertainty, whereas the scattering contribution is based
on an explicit 2% modelling assumption. These two forms of evidence
remain identified separately in the generated datasets.

## 2025 Ultrapure-Water Attenuation Benchmark

The calculated pure-water attenuation coefficient was compared with an
independent measurement reported by Cai et al. (2025).

The study used an ACS dual-channel spectrophotometer to measure absorption
and total attenuation over 400–750 nm. For ultrapure water at 532 nm, the
reported total beam attenuation coefficient was:

$$
c_{\mathrm{measured}}(532\ \mathrm{nm})
=
0.04502\ \mathrm{m^{-1}}.
$$

The corresponding OceanSenseAI calculation used the source-reported
absorption coefficient:

$$
a(532\ \mathrm{nm})
=
0.04330\ \mathrm{m^{-1}},
$$

together with the calculated pure-water molecular-scattering coefficient.
The resulting total attenuation was approximately:

$$
c_{\mathrm{model}}(532\ \mathrm{nm})
=
0.04481\ \mathrm{m^{-1}}.
$$

The signed relative difference was:

$$
\frac{
c_{\mathrm{model}}-c_{\mathrm{measured}}
}{
c_{\mathrm{measured}}
}
\times100\%
=
-0.469\%.
$$

The absolute relative difference was therefore:

$$
0.469\%.
$$

![Cai et al. 2025 ultrapure-water attenuation benchmark](../figures/study_01/cai_2025_ultrapure_water_532nm_benchmark.png)

The comparison shows close agreement between the calculated attenuation
coefficient and the published ACS measurement at 532 nm.

This result must be interpreted as a single-wavelength benchmark rather
than a complete spectral validation. The publication does not report an
uncertainty for the stated 532 nm value, and the experimental conditions
are not identical to those associated with the absorption and scattering
inputs used by OceanSenseAI.

The benchmark therefore provides an independent modern point check of the
total attenuation calculation but does not replace full-spectrum
comparison against an independent absorption dataset.

## Independent Pure-Water Absorption Dataset Benchmark

The sensitivity of the calculated pure-water attenuation spectrum to the
selected absorption dataset was assessed using measurements reported by
Sogandares and Fry (1997).

Their dataset contains pure-water absorption measurements from 340 to
640 nm at 10 nm intervals. The measurements were obtained at
\(25^\circ\mathrm{C}\) using photothermal deflection spectroscopy, a
method designed to measure absorption without requiring a scattering
correction.

The Sogandares and Fry absorption spectrum was compared with the
Mason, Cone, and Fry dataset already used in OceanSenseAI. The
comparison was restricted to the 21 exact common wavelengths from
350 to 550 nm at 10 nm intervals.

No interpolation was applied. The original source datasets remained
unchanged.

The two studies were performed at different temperatures and used
different measurement methods:

| Dataset | Temperature | Measurement method |
|---|---:|---|
| Mason, Cone, and Fry (2016) | \(23\pm0.5^\circ\mathrm{C}\) | Integrating-cavity absorption measurement |
| Sogandares and Fry (1997) | \(25^\circ\mathrm{C}\) | Photothermal deflection spectroscopy |

The source-reported absorption spectra are compared below.

![Independent pure-water absorption dataset benchmark](../figures/study_01/pure_water_absorption_dataset_benchmark.png)

On the common 10 nm wavelength grid, the minimum absorption values were:

| Dataset | Minimum wavelength | Absorption coefficient |
|---|---:|---:|
| Mason, Cone, and Fry (2016) | 350 nm | \(0.000890\ \mathrm{m^{-1}}\) |
| Sogandares and Fry (1997) | 420 nm | \(0.006200\ \mathrm{m^{-1}}\) |

The minimum reported for the Mason dataset over its complete original
wavelength grid remains at 344 nm. The 350 nm value reported here is only
the minimum on the restricted common 10 nm comparison grid.

For each common wavelength, the absorption difference was calculated as:

$$
\Delta a(\lambda)
=
a_{\mathrm{Sogandares}}(\lambda)
-
a_{\mathrm{Mason}}(\lambda),
$$

and the relative difference was calculated with the Mason value as the
reference:

$$
\Delta_{\%}(\lambda)
=
\frac{
a_{\mathrm{Sogandares}}(\lambda)
-
a_{\mathrm{Mason}}(\lambda)
}{
a_{\mathrm{Mason}}(\lambda)
}
\times100\%.
$$

Across the 21 common wavelengths, the mean absolute relative absorption
difference was:

$$
299.61\%,
$$

while the median absolute relative difference was:

$$
29.95\%.
$$

The mean is substantially larger than the median because the datasets
differ strongly at the shorter wavelengths, where the Mason absorption
coefficients are particularly small. Relative differences therefore
become very large even when the absolute differences remain moderate.

The uncertainty reported by both sources was combined as:

$$
u_{\Delta a}(\lambda)
=
\sqrt{
u_{\mathrm{Mason}}^2(\lambda)
+
u_{\mathrm{Sogandares}}^2(\lambda)
}.
$$

Only 4 of the 21 common wavelengths differed by no more than two combined
source uncertainties. The disagreement between the datasets therefore
cannot generally be explained by their reported uncertainty intervals
alone.

To evaluate the effect on total beam attenuation, the molecular-scattering
model was added separately to each absorption dataset at its corresponding
measurement temperature:

$$
c(\lambda,T)
=
a(\lambda)
+
b(\lambda,T).
$$

The resulting attenuation spectra are shown below.

![Sensitivity of total attenuation to absorption dataset](../figures/study_01/pure_water_attenuation_dataset_sensitivity.png)

On the common 10 nm grid, the calculated total-attenuation minima were:

| Absorption source | Scattering-model temperature | Minimum wavelength | Minimum attenuation |
|---|---:|---:|---:|
| Mason, Cone, and Fry (2016) | \(23^\circ\mathrm{C}\) | 410 nm | \(0.007188\ \mathrm{m^{-1}}\) |
| Sogandares and Fry (1997) | \(25^\circ\mathrm{C}\) | 430 nm | \(0.010095\ \mathrm{m^{-1}}\) |

The Mason-based minimum differs slightly from the previously reported
416 nm result because this comparison uses only the common 10 nm
wavelength grid. The earlier 416 nm result was obtained using the full
2 nm Mason dataset.

The benchmark shows that the predicted wavelength and magnitude of
minimum total attenuation depend materially on the selected absorption
dataset. The preferred wavelength shifts from 410 nm to 430 nm on the
common grid, while the minimum attenuation coefficient also increases.

This result does not establish that one dataset is universally correct
and the other is incorrect. The measurements differ in sample
preparation, experimental method, temperature, spectral resolution, and
possible contamination sensitivity.

The result instead demonstrates that absorption-dataset selection is an
important source of model uncertainty. Conclusions about optimum
wavelength and achievable propagation distance should therefore not be
based on a single absorption dataset without sensitivity analysis.

---

## Current Status

| Task | Status |
|---|---|
| Research question | Complete |
| Model scope | Complete |
| Mathematical formulation | Complete |
| Verification requirements | Complete |
| Experimental attenuation benchmark | Complete |
| Water-type parameter extraction | Complete |
| Parameter provenance and consistency checks | Complete |
| Beer–Lambert implementation | Complete |
| Automated propagation tests | Complete |
| Distance-sweep analysis | Complete |
| Water-type comparison | Complete |
| Pure-water spectral absorption dataset | Complete |
| Spectral dataset validation | Complete |
| Pure-water absorption analysis | Complete |
| Wavelength-dependent molecular-scattering model | Complete |
| Scattering-model validation against Morel measurements | Complete |
| Molecular-scattering spectrum | Complete |
| Total pure-water spectral attenuation analysis | Complete |
| Combined attenuation dataset and figure | Complete |
| GitHub Actions workflow | Complete |
| Wavelength–distance transmission analysis | Complete |
| Combined uncertainty propagation | Complete |
| 2025 ultrapure-water attenuation benchmark | Complete |
| Independent pure-water absorption dataset benchmark | Complete |
| Absorption-dataset sensitivity analysis | Complete |
| Study 01 baseline channel characterisation | Complete |

---

## Next Step — Study 02: Receiver, Noise, and Link Budget

Study 01 established and validated the baseline direct-path optical
channel model. It examined absorption, molecular scattering, total beam
attenuation, wavelength dependence, propagation distance, uncertainty,
and sensitivity to the selected absorption dataset.

The next stage will connect the optical channel model to a basic receiver
and electrical signal model.

The received optical power will first be written as:

$$
P_r(L,\lambda)
=
P_t(\lambda)
G_{\mathrm{sys}}(L,\lambda)
e^{-c(\lambda)L},
$$

where \(G_{\mathrm{sys}}\) will represent the geometric and receiver
factors that were excluded from Study 01.

Study 02 will introduce:

- transmitted optical power;
- beam divergence;
- receiver aperture;
- transmitter–receiver separation;
- geometric collection efficiency;
- detector responsivity;
- received photocurrent;
- background optical power;
- shot noise;
- thermal noise;
- electrical bandwidth;
- signal-to-noise ratio;
- a reproducible optical link-budget calculation.

The photodetector output current will be modelled initially as:

$$
I_s
=
R(\lambda)P_r,
$$

where \(R(\lambda)\) is the detector responsivity.

The corresponding electrical signal power will depend on the selected
receiver model and load resistance. Noise contributions will be kept
separate so that their physical origins remain traceable.

The initial shot-noise variance will be represented as:

$$
\sigma_{\mathrm{shot}}^2
=
2q
\left(
I_s+I_{\mathrm{background}}+I_{\mathrm{dark}}
\right)
B,
$$

where:

- \(q\) is the elementary charge;
- \(I_s\) is the signal photocurrent;
- \(I_{\mathrm{background}}\) is the background-light photocurrent;
- \(I_{\mathrm{dark}}\) is the detector dark current;
- \(B\) is the electrical bandwidth.

A basic thermal-noise model will then be added using explicitly recorded
receiver parameters and assumptions.

The resulting signal-to-noise ratio will be calculated as:

$$
\mathrm{SNR}
=
\frac{
I_s^2
}{
\sigma_{\mathrm{shot}}^2
+
\sigma_{\mathrm{thermal}}^2
}.
$$

The first Study 02 implementation will use a simple monochromatic
line-of-sight receiver model. More complex effects such as turbulence,
multiple scattering, pointing errors, detector saturation, and
time-varying channel behaviour will remain outside the initial scope.

After the receiver and noise model has been verified, the project will
begin basic signal processing using:

- generated binary data;
- on–off keying;
- noisy received waveforms;
- threshold detection;
- recovered bit sequences;
- bit-error-rate calculation;
- basic filtering and detector comparison.

This sequence ensures that signal-processing results are based on a
physically traceable optical channel, receiver, and noise model rather
than on arbitrary simulated noise.