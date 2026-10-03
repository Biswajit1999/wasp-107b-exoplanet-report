# Data provenance

All six inputs are public products from Zenodo record
[17085766](https://doi.org/10.5281/zenodo.17085766), version 1, published
2025-09-15 by Krishnamurthy et al. for the WASP-107 b NIRISS-SOSS analysis.

- `niriss_soss_order1_transmission_spectrum.txt` and
  `niriss_soss_order2_transmission_spectrum.txt` are renamed copies of the
  exoTEDRF broad transmission orders. Columns are wavelength [µm], fractional
  transit depth, and 1-sigma uncertainty.
- `W107b_SCARLET_NIRISS_krishnamurthy_etal.txt` is the released best-fit
  SCARLET model: wavelength [µm] and transit depth [ppm].
- `W107b_helium_transmission_NIRISS_krishnamurthy_etal.txt` is the R≈700
  helium-triplet spectrum: wavelength, wavelength error, depth [ppm], and
  depth error [ppm].
- The two `W107b_binned_*Helium*lightcurve.txt` files are the observed helium
  light curve and EvE thermosphere model: hours from mid-transit and normalized
  flux. The observed release contains no flux-uncertainty column.

`source_manifest.json` records every Zenodo MD5 and an LF-normalized SHA-256
digest. Run `python scripts/validate_sources.py` to verify the local copies.
