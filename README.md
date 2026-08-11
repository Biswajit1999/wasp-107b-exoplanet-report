# WASP-107 b — Exoplanet Atmosphere Report

A puffy, low-density warm Neptune, and one of the clearest real JWST atmospheric
detections to date: photochemically produced sulfur dioxide, with a surprising
deficit of methane. This repo pulls real system parameters and a real reduced
JWST transmission spectrum — nothing here is a synthetic placeholder.

**[Open the full report](index.html)** (open locally in a browser, or serve with
`python -m http.server` from this directory).

## What's real here

- **System parameters** — queried live from the NASA Exoplanet Archive TAP
  service (`pscomppars` table) for `WASP-107 b`.
- **Transmission spectrum** — the actual reduced JWST NIRISS SOSS transit-depth
  vs. wavelength data (spectral orders 1 and 2), released publicly by
  Krishnamurthy et al. on Zenodo (record
  [10.5281/zenodo.17085766](https://doi.org/10.5281/zenodo.17085766)). See
  `data/` for the raw files exactly as downloaded.
- **Analysis** — `scripts/analyze_spectrum.py` loads the real data, computes a
  weighted mean transit depth, RMS scatter, and peak-to-trough amplitude, and
  produces the spectrum + residuals figure in `figures/`. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    real reduced JWST NIRISS SOSS spectrum files (Zenodo)
scripts/analyze_spectrum.py   real analysis producing the figure + statistics
figures/                 generated plot + summary_statistics.csv
```

## Key finding this repo shows directly

143 real wavelength bins across 0.6-2.8 microns, weighted mean transit depth
2.062% ± 0.0004%, with a clear water-vapor-consistent rise toward the
spectrum's blue and red edges. The SO2/methane-depletion results (Dyrek et
al. 2024) come from separate MIRI observations not included in this NIRISS
dataset — stated explicitly so this repo doesn't overclaim what one
instrument's data shows.

## References

1. Dyrek, A. et al., 2024. SO2, silicate clouds, but no CH4 detected in a warm
   Neptune with JWST. *Nature*, 625, pp.51-54.
2. Krishnamurthy, V. et al. NIRISS-SOSS transmission-spectrum reduction of
   WASP-107 b. Zenodo record
   [10.5281/zenodo.17085766](https://doi.org/10.5281/zenodo.17085766).
3. Piaulet, C. et al., 2021. Evidence for a Large, Hot Core in the Warm
   Neptune WASP-107 b. *The Astronomical Journal*, 161, 70.
4. Sing, D.K. et al., 2019. Helium in the eroding atmosphere of an exoplanet.
   *The Astronomical Journal*, 158, 91.
5. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/> —
   system parameters, queried live via TAP.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
