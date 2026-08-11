# Data source

`niriss_soss_order1_transmission_spectrum.txt` and
`niriss_soss_order2_transmission_spectrum.txt` are downloaded, unmodified,
from Zenodo record **10.5281/zenodo.17085766** — "WASP-107b NIRISS-SOSS
data - Krishnamurthy et al." — files `W107b_exoTEDRF_NIRISS_SOSS_O1.txt`
and `W107b_exoTEDRF_NIRISS_SOSS_O2.txt`.

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/17085766`.

Each file has three whitespace-separated columns with no header:

1. wavelength [micron]
2. transit depth, (Rp/Rs)^2
3. 1-sigma uncertainty on the transit depth

Order 1 covers roughly 0.85-2.8 micron; order 2 covers roughly 0.6-0.85
micron (the two SOSS diffraction orders from the same observation).
