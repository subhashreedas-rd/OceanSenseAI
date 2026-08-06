# Study 03A — Photon-Budget Modelling

## Status

**Implemented and numerically verified as a baseline photon-budget study.**

This study connects the existing underwater optical link model to mean photon numbers. It does not yet simulate individual detector clicks, photon-count probability distributions, state preparation, measurement protocols, or secure-key generation.

---

## 1. Scientific Question

> How do received optical power, optical wavelength, bit duration, and detector efficiency determine the mean number of photons available during each transmitted bit?

---

## 2. Motivation

Studies 01 and 02 represent the optical signal mainly through:

- optical power in watts;
- detector current in amperes;
- electrical noise variance;
- signal-to-noise ratio;
- recovered classical bits.

Optical power is a continuous average quantity. However, light exchanges energy with matter in discrete packets called photons.

The purpose of Study 03A is to connect these two descriptions:

```text
Received optical power
        ↓
Energy received during one bit
        ↓
Energy carried by one photon
        ↓
Mean photons reaching the detector
        ↓
Mean photons successfully detected
```

This conversion is necessary before developing a discrete photon-counting receiver.

---

## 3. Scope of the Study

Study 03A is a **photon-budget calculation**.

It calculates:

- the energy of one photon;
- the optical energy received during one bit;
- the mean number of photons reaching the detector;
- an estimated detector efficiency derived from responsivity;
- the mean number of detected photons;
- the dependence of these quantities on propagation distance.

The study does not model:

- individual random photon arrivals;
- Poisson photon-count statistics;
- click and no-click detector outcomes;
- detector dead time;
- afterpulsing;
- timing jitter;
- background photon counts;
- dark-count events;
- state preparation or measurement;
- communication security.

The calculated photon numbers are expected or mean values. They are not guaranteed integer counts for an individual bit.

---

## 4. Connection to the Existing Studies

### Study 01

Study 01 provides the wavelength-dependent direct-path attenuation model:

$$
T_{\mathrm{water}}(L,\lambda)
=
e^{-c(\lambda)L}.
$$

This determines what fraction of the optical beam survives propagation through water.

### Study 02

Study 02 combines water attenuation with transmitter and receiver geometry:

$$
P_r
=
P_t
\eta_{\mathrm{sys}}
\eta_g
e^{-cL}.
$$

The result is the received optical power:

$$
P_r.
$$

### Study 03A

Study 03A converts this received power into mean photon numbers:

$$
P_r
\rightarrow
\mu_r
\rightarrow
\mu_d,
$$

where:

- $\mu_r$ is the mean number of photons reaching the detector during one bit;
- $\mu_d$ is the mean number of photons successfully detected during one bit.

---

## 5. Physical Model

### 5.1 Energy of One Photon

The energy of one photon is:

$$
E_\gamma
=
\frac{hc}{\lambda},
$$

where:

- $E_\gamma$ is photon energy in joules;
- $h$ is Planck’s constant;
- $c$ is the speed of light in vacuum;
- $\lambda$ is optical wavelength in metres.

The constants used are exact SI values:

$$
h
=
6.62607015\times10^{-34}
\ \mathrm{J\,s},
$$

and:

$$
c
=
299\,792\,458
\ \mathrm{m/s}.
$$

Photon energy is inversely proportional to wavelength:

$$
E_\gamma\propto\frac{1}{\lambda}.
$$

Therefore, shorter-wavelength photons carry more energy than longer-wavelength photons.

At the baseline wavelength of $416\ \mathrm{nm}$:

$$
E_\gamma
\approx
4.77511\times10^{-19}
\ \mathrm{J}.
$$

---

### 5.2 Bit Duration

The duration of one bit is determined by the bit rate:

$$
T_b
=
\frac{1}{R_b},
$$

where:

- $T_b$ is bit duration in seconds;
- $R_b$ is bit rate in bits per second.

For the baseline bit rate:

$$
R_b
=
20\times10^6
\ \mathrm{bit/s},
$$

the bit duration is:

$$
T_b
=
\frac{1}{20\times10^6}
=
5.0\times10^{-8}
\ \mathrm{s}.
$$

Therefore:

$$
T_b=50\ \mathrm{ns}.
$$

---

### 5.3 Energy Received During One Bit

Optical power is energy transferred per unit time:

$$
P
=
\frac{E}{t}.
$$

Rearranging gives:

$$
E=Pt.
$$

The energy received during one bit is therefore:

$$
E_{\mathrm{bit}}
=
P_rT_b,
$$

where:

- $P_r$ is received optical power;
- $T_b$ is bit duration;
- $E_{\mathrm{bit}}$ is the received optical energy during one bit.

---

### 5.4 Mean Received Photons per Bit

The mean number of photons corresponding to the received energy is:

$$
\mu_r
=
\frac{E_{\mathrm{bit}}}{E_\gamma}.
$$

Substituting:

$$
E_{\mathrm{bit}}=P_rT_b
$$

and:

$$
E_\gamma=\frac{hc}{\lambda},
$$

gives:

$$
\mu_r
=
\frac{P_rT_b}
{hc/\lambda}.
$$

Therefore:

$$
\boxed{
\mu_r
=
\frac{P_rT_b\lambda}{hc}
}
$$

This equation shows that the mean received photon number increases when:

- received optical power increases;
- bit duration increases;
- wavelength increases.

However, wavelength also changes underwater attenuation and detector response. It cannot be optimised using photon energy alone.

---

### 5.5 Detector Efficiency from Responsivity

Study 02 specifies detector responsivity:

$$
R
=
0.30
\ \mathrm{A/W}.
$$

For a unity-gain detector, responsivity and external detection efficiency are related by:

$$
R
=
\eta_d
\frac{q}{E_\gamma},
$$

where:

- $R$ is detector responsivity;
- $\eta_d$ is external detection efficiency;
- $q$ is the elementary charge;
- $E_\gamma$ is photon energy.

Rearranging:

$$
\boxed{
\eta_d
=
\frac{RE_\gamma}{q}
}
$$

The elementary charge is:

$$
q
=
1.602176634\times10^{-19}
\ \mathrm{C}.
$$

For the baseline wavelength and responsivity:

$$
\eta_d
\approx
0.8941.
$$

This corresponds to an estimated efficiency of approximately:

$$
89.4\%.
$$

This conversion assumes:

- one collected electron per successfully detected photon;
- no internal multiplication gain;
- responsivity corresponding to the same wavelength;
- linear detector operation.

The result should therefore be interpreted as a baseline responsivity-derived estimate, not as a measured photon-counting-detector efficiency.

---

### 5.6 Mean Detected Photons per Bit

The mean detected photon number is:

$$
\boxed{
\mu_d
=
\eta_d\mu_r
}
$$

where:

- $\mu_r$ is the mean incident photon number;
- $\eta_d$ is detection efficiency;
- $\mu_d$ is the mean detected photon number.

A value such as:

$$
\mu_d=10
$$

does not mean exactly ten photons will be detected during every bit.

It means that repeated identical bit intervals would produce ten detected photons per bit on average under the model assumptions.

---

## 6. Baseline Parameters

| Parameter | Symbol | Value | Status |
|---|---:|---:|---|
| Wavelength | $\lambda$ | $416\ \mathrm{nm}$ | Reused from Study 01 baseline |
| Attenuation coefficient | $c$ | $7.1351\times10^{-3}\ \mathrm{m^{-1}}$ | Reused from Study 01 baseline |
| Transmitted optical power | $P_t$ | $0.1\ \mathrm{W}$ | Study 02 assumption |
| Initial beam radius | $w_0$ | $0.01\ \mathrm{m}$ | Study 02 assumption |
| Divergence half-angle | $\theta$ | $5.0\times10^{-3}\ \mathrm{rad}$ | Study 02 assumption |
| Receiver radius | $r_r$ | $0.025\ \mathrm{m}$ | Study 02 assumption |
| System efficiency | $\eta_{\mathrm{sys}}$ | $0.8$ | Study 02 assumption |
| Responsivity | $R$ | $0.30\ \mathrm{A/W}$ | Study 02 assumption |
| Bit rate | $R_b$ | $20\ \mathrm{Mbit/s}$ | Study 02 waveform assumption |
| Bit duration | $T_b$ | $50\ \mathrm{ns}$ | Calculated |
| Distance range | $L$ | $0$ to $800\ \mathrm{m}$ | Study grid |
| Distance step | $\Delta L$ | $2\ \mathrm{m}$ | Study grid |

The transmitter, channel, and receiver assumptions are reused rather than redefined so that Study 03A remains directly traceable to the earlier baseline.

---

## 7. Numerical Procedure

For every propagation distance:

1. Calculate the water transmittance.
2. Calculate the expanded beam radius.
3. Calculate geometric collection efficiency.
4. Calculate received optical power using the Study 02 link-budget model.
5. Calculate the photon energy at the selected wavelength.
6. Calculate the energy received during one bit.
7. Calculate the mean photons reaching the detector.
8. Estimate detector efficiency from responsivity.
9. Calculate the mean detected photons per bit.
10. Store the results in a CSV file.
11. Plot mean photon number against distance using a logarithmic vertical axis.

The complete workflow is:

```text
Study 01 attenuation coefficient
        ↓
Study 02 received optical power
        ↓
Photon energy
        ↓
Energy received per bit
        ↓
Mean received photons per bit
        ↓
Responsivity-derived efficiency
        ↓
Mean detected photons per bit
```

---

## 8. Numerical Verification

The photon-budget implementation is verified using automated tests.

The tests check:

- photon energy at a known wavelength;
- inverse proportionality between energy and wavelength;
- doubling wavelength halves photon energy;
- received energy equals power multiplied by time;
- zero power gives zero received energy;
- mean photon number agrees with a hand-calculated case;
- detector efficiency is applied correctly;
- zero efficiency gives zero detected photons;
- unit efficiency preserves the received mean;
- photons per bit agree with direct interval calculation;
- negative and nonphysical inputs are rejected;
- nonfinite inputs are rejected.

The new photon-budget module contains 19 dedicated tests.

After integration, the complete repository test suite contained:

```text
163 tests
```

and all tests passed.

---

## 9. Baseline Results

Selected results from the distance sweep are:

| Distance | Received optical power | Mean received photons per bit | Mean detected photons per bit |
|---:|---:|---:|---:|
| $0\ \mathrm{m}$ | $8.0000\times10^{-2}\ \mathrm{W}$ | $8.3768\times10^{9}$ | $7.4898\times10^{9}$ |
| $442\ \mathrm{m}$ | $4.3313\times10^{-7}\ \mathrm{W}$ | $4.5353\times10^{4}$ | $4.0551\times10^{4}$ |
| $800\ \mathrm{m}$ | $1.0320\times10^{-8}\ \mathrm{W}$ | $1.0806\times10^{3}$ | $9.6620\times10^{2}$ |

The complete distance sweep is stored in:

```text
studies/study_03/results/photon_budget_distance_sweep.csv
```

The generated figure is stored in:

```text
figures/study_03/mean_photons_per_bit_vs_distance.png
```

---

## 10. Interpretation

The mean photon number decreases strongly with distance because the received optical power decreases through two separate mechanisms:

1. exponential attenuation in water;
2. decreasing geometric collection as the beam expands.

The detected-photon curve remains below and nearly parallel to the received-photon curve because a fixed detector efficiency is applied at every distance:

$$
\mu_d=\eta_d\mu_r.
$$

Since $\eta_d$ is constant, distance changes $\mu_r$ but does not change the fraction detected.

A major finding is that the present baseline remains a many-photon link throughout the simulated distance range.

Even at $800\ \mathrm{m}$, the model predicts approximately:

$$
10^3
$$

photons per bit reaching the detector.

Therefore, the current transmitted-power and bit-rate assumptions do not represent a single-photon or strongly photon-starved operating regime.

---

## 11. What the Study Demonstrates

Study 03A demonstrates that:

- received optical power can be converted consistently into photon energy and mean photon number;
- the existing channel and link-budget models can support photon-level energy accounting;
- propagation distance strongly reduces the photon budget;
- detector efficiency produces a proportional reduction between incident and detected photon means;
- the current baseline remains in a many-photon regime;
- a separate photon-counting model is needed before individual detection events can be studied.

---

## 12. What the Study Does Not Demonstrate

The study does not demonstrate:

- that an exact number of photons arrives during every bit;
- individual detector-click probabilities;
- photon-number fluctuations;
- low-light communication performance;
- security of any communication protocol;
- experimentally measured detector efficiency;
- operation of a practical photon-counting receiver;
- background-count or dark-count error rates;
- end-to-end experimental validation.

The mean photon budget is only the first bridge between continuous optical power and discrete detection events.

---

## 13. Limitations

### Constant optical power during each bit

The calculation assumes that received optical power remains constant over the bit duration.

### Mean-value model

Only expected photon numbers are calculated. Random photon-count variation is not yet included.

### Responsivity-derived efficiency

Detector efficiency is inferred from responsivity using a unity-gain conversion. A practical photon-counting detector may have different efficiency, dead time, timing jitter, and dark-count behaviour.

### Direct-path propagation

The received power is inherited from the direct-path Beer–Lambert link model. Delayed multiply scattered photons are not represented.

### Ideal alignment and geometry

The inherited link model assumes perfect transmitter–receiver alignment and a simplified uniform beam footprint.

### Fixed wavelength

The distance sweep uses one baseline wavelength. It does not yet compare the combined effects of wavelength-dependent photon energy, attenuation, and detector efficiency.

### Classical transmitter baseline

The transmitted power is inherited from the existing classical OOK model and is much larger than the mean optical levels normally associated with single-photon operation.

---

## 14. Reproducibility

Run the dedicated photon-budget tests using:

```bash
python -m unittest tests.test_photon_budget -v
```

Run the complete test suite using:

```bash
python -m unittest discover -s tests -v
```

Run Study 03A using:

```bash
python studies/study_03/run_photon_budget.py
```

The script regenerates the result CSV and figure.

---

## 15. Study Files

```text
src/photon_budget.py
tests/test_photon_budget.py
studies/study_03/run_photon_budget.py
studies/study_03/results/photon_budget_distance_sweep.csv
figures/study_03/mean_photons_per_bit_vs_distance.png
docs/STUDY_03.md
```

---

## 16. Next Scientific Step

The next logical extension is a photon-counting receiver in which the mean photon number becomes the parameter of a random count distribution.

That study would introduce:

- Poisson photon-count statistics;
- signal, background, and dark-count means;
- click and no-click probabilities;
- analytical count probabilities;
- Monte Carlo count generation;
- count-threshold detection;
- comparison between analytical and simulated error rates.

This extension should be developed only after the mean photon-budget model has been documented and verified.