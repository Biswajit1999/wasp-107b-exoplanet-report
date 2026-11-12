"""Conditional robustness tests for resolved helium transmission features."""
import numpy as np

def contrast_with_correlation(wavelength, depth, sigma, core=(1.082, 1.085), rho=0.0):
    """GLS core-minus-sideband contrast for assumed bin-index AR(1) covariance."""
    w, y, s = (np.asarray(a, dtype=float) for a in (wavelength, depth, sigma))
    if w.ndim != 1 or w.size < 3 or y.shape != w.shape or s.shape != w.shape:
        raise ValueError("aligned one-dimensional arrays required")
    if not all(np.all(np.isfinite(a)) for a in (w, y, s)) or np.any(s <= 0):
        raise ValueError("finite data and positive errors required")
    if np.any(np.diff(w) <= 0) or not -1 < rho < 1 or not core[0] < core[1]:
        raise ValueError("sorted wavelengths, core, and |rho|<1 required")
    mask = (w >= core[0]) & (w <= core[1])
    if not mask.any() or mask.all():
        raise ValueError("both core and sideband required")
    x = np.column_stack((np.ones(w.size), mask.astype(float)))
    i = np.arange(w.size)
    covariance = s[:, None] * s[None, :] * rho ** np.abs(i[:, None] - i[None, :])
    l = np.linalg.cholesky(covariance)
    a = np.linalg.solve(l, x)
    b = np.linalg.solve(l, y)
    normal = a.T @ a
    beta = np.linalg.solve(normal, a.T @ b)
    return float(beta[1]), float(np.sqrt(np.linalg.inv(normal)[1, 1]))

def leave_one_out_contrasts(wavelength, depth, sigma, core=(1.082, 1.085)):
    """Exact one-bin deletion contrasts with independent marginal errors."""
    w = np.asarray(wavelength)
    if w.ndim != 1:
        raise ValueError("wavelength must be one-dimensional")
    return np.asarray([
        contrast_with_correlation(np.delete(w, i), np.delete(depth, i),
                                  np.delete(sigma, i), core=core)[0]
        for i in range(w.size)
    ])
