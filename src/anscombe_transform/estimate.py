"""
Parameter estimation for Anscombe Transform codec.

This module provides functions to estimate codec parameters (photon sensitivity
and zero level) from temporal variance analysis of movie data.
"""

import numpy as np
from sklearn.linear_model import HuberRegressor as Regressor


def _longest_run(bool_array: np.ndarray) -> slice:
    """
    Find the longest contiguous segment of True values inside bool_array.

    Parameters
    ----------
    bool_array : np.ndarray
        1D boolean array.

    Returns
    -------
    slice
        Slice with start and stop for the longest contiguous block of True values.
    """
    step = np.diff(np.int8(bool_array), prepend=0, append=0)
    on = np.where(step == 1)[0]
    off = np.where(step == -1)[0]
    i = np.argmax(off - on)
    return slice(on[i], off[i])


def compute_sensitivity(movie: np.array, count_weight_gamma: float = 0.2) -> dict:
    """
    Calculate photon sensitivity and zero level from temporal variance analysis.

    This function estimates camera parameters by fitting the noise transfer function
    from temporal variance. It uses HuberRegressor to robustly fit the relationship
    between mean signal and variance.

    Parameters
    ----------
    movie : np.ndarray
        A movie in the format (time, height, width).
    count_weight_gamma : float, optional
        Weighting exponent for pixel counts in regression, by default 0.2.
        - 0.0: weigh each intensity level equally
        - 1.0: weigh each intensity in proportion to pixel counts

    Returns
    -------
    dict
        Dictionary with the following keys:

        - 'model' : HuberRegressor
            The fitted regression model.
        - 'counts' : np.ndarray
            Pixel counts per intensity bin.
        - 'min_intensity' : int
            Minimum intensity value used in fitting.
        - 'max_intensity' : int
            Maximum intensity value used in fitting.
        - 'variance' : np.ndarray
            Computed variance at each intensity level.
        - 'sensitivity' : float
            Estimated photon sensitivity (ADU per photon).
        - 'zero_level' : float
            Estimated baseline signal level with no photons.

    Raises
    ------
    AssertionError
        If movie is not 3-dimensional or if insufficient intensity range is present.
    """
    assert movie.ndim == 3, (
        f"Thee dimensions (Time x Height x Width) of grayscale movie expected, got {movie.ndim} dimensions"
    )

    # assume that negative values are due to noise
    movie = np.maximum(0, movie.astype(np.int32, copy=False))
    intensity = (movie[:-1, :, :] + movie[1:, :, :] + 1) // 2
    difference = movie[:-1, :, :].astype(np.float32) - movie[1:, :, :]

    select = intensity > 0  # discard non-positive values
    intensity = intensity[select]
    difference = difference[select]

    counts = np.bincount(intensity.flatten())
    bins = _longest_run(
        counts > 0.01 * counts.mean()
    )  # consider only bins with at least 1% of mean counts
    bins = slice(max(bins.stop * 3 // 100, bins.start), bins.stop)
    assert bins.stop - bins.start > 100, (
        "The image does not have a sufficient range of intensities to compute the noise transfer function."
    )

    counts = counts[bins]
    idx = (intensity >= bins.start) & (intensity < bins.stop)
    variance = (
        np.bincount(
            intensity[idx] - bins.start,
            weights=(difference[idx] ** 2) / 2,
        )
        / counts
    )
    model = Regressor()
    model.fit(np.c_[bins], variance, counts**count_weight_gamma)
    sensitivity = model.coef_[0]
    zero_level = -model.intercept_ / model.coef_[0]

    return dict(
        model=model,
        counts=counts,
        min_intensity=bins.start,
        max_intensity=bins.stop,
        variance=variance,
        sensitivity=sensitivity,
        zero_level=zero_level,
    )
