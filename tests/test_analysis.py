"""Validation and numerical regression tests for the NIRISS audit."""

import json

import analyze_spectrum as analysis
import numpy as np
import pytest


def test_weighted_mean_and_invalid_uncertainties():
    mean, error = analysis.weighted_mean(np.array([1.0, 2.0]), np.array([1.0, 0.5]))
    assert mean == pytest.approx(1.8)
    assert error == pytest.approx(np.sqrt(0.2))
    with pytest.raises(ValueError, match="positive"):
        analysis.weighted_mean(np.array([1.0, 2.0]), np.array([0.1, 0.0]))


def test_complete_source_product_shapes():
    wave, depth, error, order = analysis.broad_spectrum()
    assert wave.size == 143
    assert {1, 2} == set(order)
    assert np.all(np.diff(wave) > 0)
    assert np.all(np.isfinite(depth))
    assert np.all(error > 0)
    assert analysis.load_table(
        analysis.DATA_DIR / "W107b_helium_transmission_NIRISS_krishnamurthy_etal.txt", 4
    ).shape == (12, 4)


def test_helium_core_contrast_regression():
    helium = analysis.load_table(
        analysis.DATA_DIR / "W107b_helium_transmission_NIRISS_krishnamurthy_etal.txt", 4
    )
    result = analysis.helium_contrast(helium)
    assert result["peak_depth_ppm"] == pytest.approx(23952.83443)
    assert result["core_minus_sideband_ppm"] == pytest.approx(1685.42, abs=0.02)
    assert result["diagonal_contrast_sigma"] == pytest.approx(24.082, abs=0.002)


def test_scarlet_and_eve_descriptive_regressions():
    wave, depth, error, _ = analysis.broad_spectrum()
    _, scarlet = analysis.compare_scarlet(wave, depth, error)
    assert scarlet["standardized_residual_rms"] == pytest.approx(1.826, abs=0.002)
    observed = analysis.load_table(analysis.DATA_DIR / "W107b_binned_Helium_lightcurve_exoTEDRF.txt", 2)
    model = analysis.load_table(analysis.DATA_DIR / "W107b_binned_EvE_Helium_model_lightcurve.txt", 2)
    _, diagnostic = analysis.lightcurve_diagnostic(observed, model)
    assert diagnostic["model_residual_rms_ppm"] == pytest.approx(312.08, abs=0.02)


def test_main_writes_structured_results():
    analysis.main()
    summary = json.loads((analysis.FIG_DIR / "analysis_summary.json").read_text(encoding="utf-8"))
    assert summary["broad_spectrum"]["n_bins"] == 143
    assert summary["helium_spectrum"]["n_bins"] == 12
    assert (analysis.FIG_DIR / "broad_spectrum_residuals.csv").is_file()
