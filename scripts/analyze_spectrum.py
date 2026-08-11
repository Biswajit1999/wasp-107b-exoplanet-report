"""Analyze the real JWST NIRISS SOSS transmission spectrum of WASP-107 b.

Data source: Krishnamurthy et al., NIRISS-SOSS reduction of WASP-107 b
(Zenodo record 17085766, files W107b_exoTEDRF_NIRISS_SOSS_O1.txt / O2.txt),
retrieved directly from Zenodo. Columns are wavelength [micron],
transit depth (Rp/Rs)^2, and its 1-sigma uncertainty.

This script computes real summary statistics from the data (no fabricated
numbers) and produces a publication-style transmission-spectrum figure with
error bars, plus a residual-vs-wavelength panel showing scatter relative to
the weighted mean depth -- the same first-look diagnostic used before fitting
any atmospheric model to a real spectrum.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def load_order(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    wavelength, depth, error = [], [], []
    with path.open() as handle:
        for line in handle:
            parts = line.split()
            if len(parts) != 3:
                continue
            w, d, e = map(float, parts)
            wavelength.append(w)
            depth.append(d)
            error.append(e)
    return np.array(wavelength), np.array(depth), np.array(error)


def weighted_mean(depth: np.ndarray, error: np.ndarray) -> tuple[float, float]:
    weights = 1.0 / error**2
    mean = np.sum(depth * weights) / np.sum(weights)
    mean_error = np.sqrt(1.0 / np.sum(weights))
    return mean, mean_error


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    w1, d1, e1 = load_order(DATA_DIR / "niriss_soss_order1_transmission_spectrum.txt")
    w2, d2, e2 = load_order(DATA_DIR / "niriss_soss_order2_transmission_spectrum.txt")

    wavelength = np.concatenate([w2, w1])
    depth = np.concatenate([d2, d1])
    error = np.concatenate([e2, e1])
    order = np.argsort(wavelength)
    wavelength, depth, error = wavelength[order], depth[order], error[order]

    mean_depth, mean_depth_error = weighted_mean(depth, error)
    scatter_rms = np.std(depth)
    peak_depth = depth.max()
    peak_wavelength = wavelength[depth.argmax()]
    trough_depth = depth.min()
    trough_wavelength = wavelength[depth.argmin()]
    amplitude_ppm = (peak_depth - trough_depth) * 1e6

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_wavelength_bins", len(wavelength), "count"])
        writer.writerow(["wavelength_min", f"{wavelength.min():.4f}", "micron"])
        writer.writerow(["wavelength_max", f"{wavelength.max():.4f}", "micron"])
        writer.writerow(["weighted_mean_transit_depth", f"{mean_depth:.6f}", "(Rp/Rs)^2"])
        writer.writerow(["weighted_mean_transit_depth_error", f"{mean_depth_error:.6f}", "(Rp/Rs)^2"])
        writer.writerow(["depth_scatter_rms", f"{scatter_rms:.6f}", "(Rp/Rs)^2"])
        writer.writerow(["peak_depth", f"{peak_depth:.6f}", "(Rp/Rs)^2"])
        writer.writerow(["peak_wavelength", f"{peak_wavelength:.4f}", "micron"])
        writer.writerow(["trough_depth", f"{trough_depth:.6f}", "(Rp/Rs)^2"])
        writer.writerow(["trough_wavelength", f"{trough_wavelength:.4f}", "micron"])
        writer.writerow(["peak_to_trough_amplitude", f"{amplitude_ppm:.1f}", "ppm"])

    plt.style.use("default")
    fig, (ax_spec, ax_resid) = plt.subplots(
        2, 1, figsize=(9, 6.5), sharex=True, height_ratios=[2.4, 1], gridspec_kw={"hspace": 0.08}
    )

    ax_spec.errorbar(
        wavelength, depth * 1e2, yerr=error * 1e2,
        fmt="o", ms=3.4, color="#1f6f5c", ecolor="#8fbfb1", elinewidth=1, capsize=0,
        label="WASP-107 b, JWST NIRISS SOSS (Krishnamurthy et al.)",
    )
    ax_spec.axhline(mean_depth * 1e2, color="#c0562a", lw=1.2, ls="--", label="weighted mean depth")
    ax_spec.set_ylabel(r"Transit depth $(R_p/R_s)^2$ [%]")
    ax_spec.set_title("WASP-107 b transmission spectrum (JWST NIRISS SOSS, real reduced data)")
    ax_spec.legend(loc="upper right", fontsize=8, frameon=False)
    ax_spec.grid(alpha=0.25)

    residual_ppm = (depth - mean_depth) * 1e6
    ax_resid.errorbar(
        wavelength, residual_ppm, yerr=error * 1e6,
        fmt="o", ms=3.0, color="#2c5f8a", ecolor="#9fbfd8", elinewidth=1, capsize=0,
    )
    ax_resid.axhline(0, color="#555555", lw=1)
    ax_resid.set_xlabel("Wavelength [micron]")
    ax_resid.set_ylabel("Residual [ppm]")
    ax_resid.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "wasp107b_transmission_spectrum.png", dpi=200)
    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'wasp107b_transmission_spectrum.png'}")
    print(
        f"n={len(wavelength)} points, weighted mean depth = {mean_depth*1e2:.4f}% "
        f"+/- {mean_depth_error*1e2:.4f}%, peak-to-trough amplitude = {amplitude_ppm:.0f} ppm"
    )


if __name__ == "__main__":
    main()
