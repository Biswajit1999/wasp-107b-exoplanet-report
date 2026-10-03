"""Audit the six public WASP-107 b NIRISS/SOSS science products.

The broad-band spectrum, SCARLET model, R~700 helium spectrum, helium light
curve, and EvE thermosphere model are from Zenodo record 17085766. Derived
statistics are descriptive reproductions; publication-level retrieval and
detection claims remain those of Krishnamurthy et al. (2025/2026).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"


def load_table(path: Path, ncols: int) -> np.ndarray:
    rows: list[list[float]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            try:
                rows.append([float(value) for value in line.split()[:ncols]])
            except ValueError:
                continue
    data = np.asarray(rows, dtype=float)
    if data.ndim != 2 or data.shape[1] != ncols or not np.all(np.isfinite(data)):
        raise ValueError(f"Invalid {ncols}-column table: {path}")
    return data


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    if values.shape != errors.shape or values.size == 0:
        raise ValueError("values and uncertainties must be non-empty and aligned")
    if np.any(~np.isfinite(values)) or np.any(~np.isfinite(errors)) or np.any(errors <= 0):
        raise ValueError("values must be finite and uncertainties finite and positive")
    weights = errors**-2
    return float(np.sum(values * weights) / np.sum(weights)), float(np.sum(weights) ** -0.5)


def broad_spectrum() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    products = []
    for order, filename in [(1, "niriss_soss_order1_transmission_spectrum.txt"),
                            (2, "niriss_soss_order2_transmission_spectrum.txt")]:
        table = load_table(DATA_DIR / filename, 3)
        products.append(np.column_stack((table, np.full(table.shape[0], order))))
    combined = np.vstack(products)
    combined = combined[np.argsort(combined[:, 0])]
    return combined[:, 0], combined[:, 1], combined[:, 2], combined[:, 3].astype(int)


def compare_scarlet(wave: np.ndarray, depth: np.ndarray, error: np.ndarray) -> tuple[np.ndarray, dict[str, float | int]]:
    model = load_table(DATA_DIR / "W107b_SCARLET_NIRISS_krishnamurthy_etal.txt", 2)
    prediction = np.interp(wave, model[:, 0], model[:, 1]) / 1e6
    offset, offset_error = weighted_mean(depth - prediction, error)
    residual = depth - prediction - offset
    standardized = residual / error
    return prediction + offset, {
        "n_bins": int(depth.size),
        "fitted_offset_ppm": offset * 1e6,
        "fitted_offset_error_ppm": offset_error * 1e6,
        "diagonal_chi2": float(np.sum(standardized**2)),
        "diagonal_chi2_per_bin": float(np.mean(standardized**2)),
        "standardized_residual_rms": float(np.sqrt(np.mean(standardized**2))),
        "residual_rms_ppm": float(np.sqrt(np.mean(residual**2)) * 1e6),
    }


def helium_contrast(helium: np.ndarray) -> dict[str, float | int]:
    wave, _, depth, error = helium.T
    core = (wave >= 1.082) & (wave <= 1.085)
    core_depth, core_error = weighted_mean(depth[core], error[core])
    side_depth, side_error = weighted_mean(depth[~core], error[~core])
    contrast_error = float(np.hypot(core_error, side_error))
    peak = int(np.argmax(depth))
    return {
        "n_bins": int(depth.size), "core_n_bins": int(np.count_nonzero(core)),
        "core_definition_micron": "1.082–1.085",
        "core_weighted_depth_ppm": core_depth, "core_weighted_error_ppm": core_error,
        "sideband_weighted_depth_ppm": side_depth, "sideband_weighted_error_ppm": side_error,
        "core_minus_sideband_ppm": core_depth - side_depth,
        "core_minus_sideband_error_ppm": contrast_error,
        "diagonal_contrast_sigma": (core_depth - side_depth) / contrast_error,
        "peak_wavelength_micron": float(wave[peak]), "peak_depth_ppm": float(depth[peak]),
        "peak_error_ppm": float(error[peak]),
    }


def lightcurve_diagnostic(observed: np.ndarray, model: np.ndarray) -> tuple[np.ndarray, dict[str, float | int]]:
    prediction = np.interp(observed[:, 0], model[:, 0], model[:, 1])
    residual = observed[:, 1] - prediction
    minimum = int(np.argmin(observed[:, 1]))
    return prediction, {
        "n_observed_bins": int(observed.shape[0]), "n_model_samples": int(model.shape[0]),
        "time_min_hours": float(observed[:, 0].min()), "time_max_hours": float(observed[:, 0].max()),
        "minimum_flux": float(observed[minimum, 1]),
        "minimum_flux_time_hours": float(observed[minimum, 0]),
        "model_residual_rms_ppm": float(np.sqrt(np.mean(residual**2)) * 1e6),
        "model_residual_median_absolute_ppm": float(np.median(np.abs(residual)) * 1e6),
        "uncertainty_note": "archive light curve has no uncertainty column; no goodness-of-fit probability computed",
    }


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    wave, depth, error, order = broad_spectrum()
    mean, mean_error = weighted_mean(depth, error)
    model_at_data, scarlet = compare_scarlet(wave, depth, error)
    helium = load_table(DATA_DIR / "W107b_helium_transmission_NIRISS_krishnamurthy_etal.txt", 4)
    helium_stats = helium_contrast(helium)
    lightcurve = load_table(DATA_DIR / "W107b_binned_Helium_lightcurve_exoTEDRF.txt", 2)
    eve = load_table(DATA_DIR / "W107b_binned_EvE_Helium_model_lightcurve.txt", 2)
    _, lightcurve_stats = lightcurve_diagnostic(lightcurve, eve)

    summary = {
        "source": "https://doi.org/10.5281/zenodo.17085766",
        "broad_spectrum": {
            "n_bins": int(wave.size), "wavelength_min_micron": float(wave.min()),
            "wavelength_max_micron": float(wave.max()), "weighted_mean_depth": mean,
            "weighted_mean_depth_error": mean_error, "scarlet_shape_diagnostic": scarlet,
        },
        "helium_spectrum": helium_stats,
        "helium_lightcurve": lightcurve_stats,
        "interpretation": "descriptive reproduction; use published retrieval/detection analysis for physical inference",
    }
    (FIG_DIR / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with (FIG_DIR / "summary_statistics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["n_wavelength_bins", wave.size, "count"])
        writer.writerow(["weighted_mean_transit_depth", mean, "(Rp/Rs)^2"])
        writer.writerow(["weighted_mean_transit_depth_error", mean_error, "(Rp/Rs)^2"])
        for key, value in helium_stats.items():
            writer.writerow([f"helium_{key}", value, "see quantity"])

    with (FIG_DIR / "broad_spectrum_residuals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wavelength_micron", "order", "depth", "uncertainty", "scarlet_plus_offset", "residual_ppm", "standardized_residual"])
        for values in zip(wave, order, depth, error, model_at_data, (depth - model_at_data) * 1e6,
                          (depth - model_at_data) / error, strict=True):
            writer.writerow(values)

    plt.rcParams.update({"font.size": 9, "axes.titleweight": "bold", "figure.facecolor": "white"})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.8), constrained_layout=True)
    ax = axes[0, 0]
    colors = {1: "#1d4ed8", 2: "#0f766e"}
    for number in (1, 2):
        mask = order == number
        ax.errorbar(wave[mask], depth[mask] * 100, yerr=error[mask] * 100, fmt="o", ms=3,
                    capsize=1, color=colors[number], alpha=0.8, label=f"SOSS order {number}")
    ax.plot(wave, model_at_data * 100, color="#c2410c", lw=1.5, label="SCARLET best fit + diagnostic offset")
    ax.set(title="A · Broad transmission spectrum", xlabel="Wavelength [µm]", ylabel="Transit depth [%]")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.18)

    ax = axes[1, 0]
    standardized = (depth - model_at_data) / error
    ax.errorbar(wave, standardized, yerr=np.ones_like(error), fmt="o", ms=3, color="#334155", alpha=0.7)
    ax.axhline(0, color="#64748b", ls=":")
    ax.axhspan(-1, 1, color="#94a3b8", alpha=0.15)
    ax.set(title="B · SCARLET shape residual diagnostic", xlabel="Wavelength [µm]", ylabel="Standardized residual")
    ax.grid(alpha=0.18)

    ax = axes[0, 1]
    hw, hwerr, hd, he = helium.T
    ax.errorbar(hw, hd, xerr=hwerr, yerr=he, fmt="o", ms=4, capsize=2, color="#7c3aed")
    ax.axvspan(1.082, 1.085, color="#f59e0b", alpha=0.18, label="Predeclared core band")
    ax.axhline(float(helium_stats["sideband_weighted_depth_ppm"]), color="#475569", ls="--", lw=1.2, label="Sideband weighted mean")
    ax.set(title="C · Metastable He I triplet at R≈700", xlabel="Wavelength [µm]", ylabel="Transit depth [ppm]")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.18)

    ax = axes[1, 1]
    ax.plot(eve[:, 0], eve[:, 1], color="#c2410c", lw=1.5, label="EvE thermosphere model")
    ax.plot(lightcurve[:, 0], lightcurve[:, 1], "o", ms=4, color="#0f766e", label="Binned helium light curve")
    ax.axvline(0, color="#64748b", ls=":", label="mid-transit")
    ax.set(title="D · Helium-band time series", xlabel="Time from mid-transit [h]", ylabel="Normalized flux")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.18)

    fig.suptitle("WASP-107 b · NIRISS/SOSS atmosphere and escape audit", fontsize=15, fontweight="bold")
    fig.savefig(FIG_DIR / "wasp107b_transmission_spectrum.png", dpi=220)
    plt.close(fig)
    print(f"Broad spectrum: {wave.size} bins; SCARLET standardized RMS={scarlet['standardized_residual_rms']:.3f}")
    print(f"Helium core contrast: {helium_stats['core_minus_sideband_ppm']:.1f} ± {helium_stats['core_minus_sideband_error_ppm']:.1f} ppm")
    print(f"EvE residual RMS: {lightcurve_stats['model_residual_rms_ppm']:.1f} ppm (no archived flux errors)")


if __name__ == "__main__":
    main()
