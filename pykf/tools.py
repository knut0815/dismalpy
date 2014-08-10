"""
Statespace Tools

Author: Chad Fulton
License: Simplified-BSD
"""
from __future__ import division, absolute_import, print_function

import numpy as np
from pykf import _statespace

try:
    from scipy.linalg.blas import find_best_blas_type
except ImportError:
    # Shim for SciPy 0.11, derived from tag=0.11 scipy.linalg.blas
    _type_conv = {'f': 's', 'd': 'd', 'F': 'c', 'D': 'z', 'G': 'z'}

    def find_best_blas_type(arrays):
        dtype, index = max(
            [(ar.dtype, i) for i, ar in enumerate(arrays)])
        prefix = _type_conv.get(dtype.char, 'd')
        return (prefix, dtype, None)


prefix_dtype_map = {
    's': np.float32, 'd': np.float64, 'c': np.complex64, 'z': np.complex128
}
prefix_statespace_map = {
    's': _statespace.sStatespace, 'd': _statespace.dStatespace,
    'c': _statespace.cStatespace, 'z': _statespace.zStatespace
}
prefix_kalman_filter_map = {
    's': _statespace.sKalmanFilter, 'd': _statespace.dKalmanFilter,
    'c': _statespace.cKalmanFilter, 'z': _statespace.zKalmanFilter
}


def companion_matrix(n, values=None):
    matrix = np.zeros((n, n))
    idx = np.diag_indices(n-1)
    idx = (idx[0], idx[1]+1)
    matrix[idx] = 1
    if values is not None:
        matrix[:, 0] = values
    return matrix


def diff(series, diff=1, seasonal_diff=None, k_seasons=1):
    differenced = np.asanyarray(series)

    # Seasonal differencing
    if seasonal_diff is not None:
        while seasonal_diff > 0:
            differenced = differenced[k_seasons:] - differenced[:-k_seasons]
            seasonal_diff -= 1

    # Simple differencing
    return np.diff(differenced, diff, axis=0)


def constrain_stationary_univariate(unconstrained):
    """
    Transform unconstrained parameters used by the optimizer to constrained
    parameters used in likelihood evaluation

    References
    ----------

    Monahan, John F. 1984.
    "A Note on Enforcing Stationarity in
    Autoregressive-moving Average Models."
    Biometrika 71 (2) (August 1): 403-404.
    """

    n = unconstrained.shape[0]
    y = np.zeros((n, n), dtype=unconstrained.dtype)
    r = unconstrained/((1+unconstrained**2)**0.5)
    for k in range(n):
        for i in range(k):
            y[k, i] = y[k-1, i] + r[k] * y[k-1, k-i-1]
        y[k, k] = r[k]
    return -y[n-1, :]


def unconstrain_stationary_univariate(constrained):
    """
    Transform constrained parameters used in likelihood evaluation
    to unconstrained parameters used by the optimizer

    References
    ----------

    Monahan, John F. 1984.
    "A Note on Enforcing Stationarity in
    Autoregressive-moving Average Models."
    Biometrika 71 (2) (August 1): 403-404.
    """
    n = constrained.shape[0]
    y = np.zeros((n, n), dtype=constrained.dtype)
    y[n-1:] = -constrained
    for k in range(n-1, 0, -1):
        for i in range(k):
            y[k-1, i] = (y[k, i] - y[k, k]*y[k, k-i-1]) / (1 - y[k, k]**2)
    r = y.diagonal()
    x = r / ((1 - r**2)**0.5)
    return x