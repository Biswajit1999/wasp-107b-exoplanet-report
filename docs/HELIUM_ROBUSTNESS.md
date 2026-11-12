# Helium contrast robustness

Two independent numerical diagnostics complement the retained WASP-107 b NIRISS audit.

1. **Conditional AR(1) covariance sensitivity.** Fit a sideband intercept and a predeclared 1.082–1.085 µm core contrast with generalized least squares. The assumed correlation is between consecutive sorted bins, not a measured spectral covariance or a function of wavelength separation. Sweep rho over plausible illustrative values, not as a fitted parameter.
2. **Exact leave-one-bin-out influence.** Delete each bin and refit the contrast using independent reported marginal uncertainties. Large changes identify bins that dominate the descriptive statistic.

Run `pytest -q tests/test_helium_robustness.py`. The tests use synthetic spectra; the repository's existing source data and published results are unchanged. For an observational application load the archived four-column helium table through `scripts/analyze_spectrum.py` and pass wavelength, depth, and depth error arrays. Do not interpret conditional sigma ratios as detection significances: the released product lacks a calibrated joint covariance, and bin selection and temporal correlations matter. AI-assisted coding was used; Biswajit Jana is the requested Git author.
