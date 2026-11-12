"""Synthetic regression tests for conditional helium robustness."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from helium_robustness import contrast_with_correlation, leave_one_out_contrasts

def test_exact_recovery():
    w = np.linspace(1.08, 1.09, 21)
    y = 100 + 12 * ((w >= 1.082) & (w <= 1.085))
    for rho in (0, .4, -.2):
        amplitude, error = contrast_with_correlation(w, y, np.ones(21) * 2, rho=rho)
        assert amplitude == pytest.approx(12, abs=1e-10)
        assert error > 0

def test_diagonal_error():
    w = np.linspace(1.08, 1.09, 21)
    mask = (w >= 1.082) & (w <= 1.085)
    _, error = contrast_with_correlation(w, np.ones(21), np.ones(21) * 3)
    assert error == pytest.approx(3 * np.sqrt(1 / mask.sum() + 1 / (~mask).sum()))

def test_deletion():
    w = np.linspace(1.08, 1.09, 21)
    y = 100 + 7 * ((w >= 1.082) & (w <= 1.085))
    assert np.allclose(leave_one_out_contrasts(w, y, np.ones(21)), 7)

def test_invalid_covariance():
    with pytest.raises(ValueError):
        contrast_with_correlation([1, 2, 3], [1, 2, 3], [1, 1, 0])
    with pytest.raises(ValueError):
        contrast_with_correlation([1, 2, 3], [1, 2, 3], [1, 1, 1], rho=1)
