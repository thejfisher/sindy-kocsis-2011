# SINDy Analysis of Kocsis et al. (2011) Weak-Measurement Photon Trajectories

**Data-driven equation discovery reveals a $\kappa(\theta - \sin\theta)$ nonlinearity in empirical photon trajectory data — structurally identical to a term independently extracted from a Teleparallel Gravity (TEGR) toy model.**

---

## Overview

This repository contains a fully reproducible analysis pipeline that:

1. Downloads and parses the **raw experimental data** from the landmark 2011 *Science* paper by Kocsis, Steinberg et al. — ["Observing the Average Trajectories of Single Photons in a Two-Slit Interferometer"](https://doi.org/10.1126/science.1202218)
2. Reconstructs photon trajectories from weak-measurement momentum data
3. Applies [PySINDy](https://github.com/dynamicslab/pysindy) (Sparse Identification of Nonlinear Dynamics) to **blindly discover** the governing differential equation

### The Key Result

PySINDy, operating without any assumed functional form, extracted:

$$\frac{dx}{dz} = -0.001 + 0.007\,x_0 - 0.001\,x_0^3 - 0.007\,\sin(x_0) + 0.001\,\cos(x_0)$$

The two dominant terms combine to:

$$\frac{dx}{dz} \approx 0.007\,(x - \sin x)$$

This $x - \sin(x)$ structure was **independently discovered** in a TEGR simulation, where a blind SINDy node extracted $\kappa(\theta - \sin\theta)$ from colliding torsion matrices — a completely different physical context.

### Reconstructed Trajectories

![Empirical Average Photon Trajectories](Kocsis_Empirical_Trajectories.png)

---

## Repository Contents

| File | Description |
|---|---|
| [`PAPER.md`](PAPER.md) | Full research findings document with methodology, results, discussion, and references |
| [`sindy_kocsis_2011.py`](sindy_kocsis_2011.py) | Heavily annotated Python script (644 lines of code + comments) |
| [`sindy_kocsis_report.json`](sindy_kocsis_report.json) | Machine-readable SINDy output (equations, features, R² score) |
| [`Kocsis_Empirical_Trajectories.png`](Kocsis_Empirical_Trajectories.png) | Reconstructed trajectory plot |
| `Kocsis_Data.zip` | Archived copy of the raw experimental data from the Steinberg lab |

---

## How to Run

```bash
# Clone
git clone https://github.com/thejfisher/sindy-kocsis-2011.git
cd sindy-kocsis-2011

# Install dependencies
pip install numpy scipy matplotlib pysindy

# Unzip the raw data
unzip Kocsis_Data.zip

# Run the analysis
python sindy_kocsis_2011.py
```

> **Note:** You may need to update the `data_dir` path in `sindy_kocsis_2011.py` to point to the unzipped `Kocsis_Data/OnlineArchive/Data/45-90 equiv both 0.05 15 sec/pics` directory on your system.

---

## Caveats

- The numerical goodness-of-fit is **R² ≈ 0.19** — modest. The significance lies in the *structural form* of the discovered equation, not in the quantitative accuracy.
- This is a **preliminary finding**, not a peer-reviewed result. Further statistical validation (cross-validation, bootstrap, null model comparison) is needed.
- The ontological status of weak-measurement "trajectories" remains debated in the physics community.

See [`PAPER.md`](PAPER.md) for a full discussion of limitations and proposed next steps.

---

## Related Work

| Resource | Link |
|---|---|
| TEGR Kinematic Antenna (simulation + SINDy) | [github.com/thejfisher/tegr-kinematic-antenna](https://github.com/thejfisher/tegr-kinematic-antenna) |
| Original raw data (Steinberg lab) | [physics.utoronto.ca/~aephraim/data/PhotonTrajectories/](http://www.physics.utoronto.ca/~aephraim/data/PhotonTrajectories/) |
| Original paper | Kocsis et al., *Science* **332**, 1170 (2011) — [DOI: 10.1126/science.1202218](https://doi.org/10.1126/science.1202218) |
| TEGR preprint | Available on Zenodo (see tegr-kinematic-antenna README) |

---

**Author:** J. Fisher · Independent Researcher · July 2026

*Comments, criticisms, and suggestions for collaboration are welcome. Open an issue or reach out via the links above.*
