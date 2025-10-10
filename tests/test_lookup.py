import numpy as np

from anscombe_transform.codec import lookup, make_anscombe_lookup

def reference_encode(x, conversion_gain, zero_level, beta, encoded_dtype):
    """
    A non-optimized reference implementation of the encoding step of the Anscombe transform codec.

    Parameters
    ----------
    x : array_like or float
        Input value(s), e.g. image intensities.
    conversion_gain : float
        The size of one photon in the input units (e.g. counts per photon).
    zero_level : float, optional
        The baseline offset of the sensor (default 0).
    beta : float, optional
        Output scaling factor in units of noise std dev.
        Must be > 0. (Default: 0.5)

    Returns
    -------
    y : ndarray or float
        Variance-stabilized output values.
    """
    if beta <= 0:
        raise ValueError("beta must be > 0")

    # Convert input to events
    x_events = (np.asarray(x) - zero_level) / conversion_gain

    # Precompute constants
    zero_slope = 1.0 / (beta * np.sqrt(3.0 / 8.0))
    offset = zero_level * zero_slope / conversion_gain

    # Piecewise transform
    y = np.where(
        x_events < 0,
        offset + x_events * zero_slope,  # linear extrapolation for negatives
        offset + (2.0 / beta) * (np.sqrt(x_events + 3.0 / 8.0) - np.sqrt(3.0 / 8.0))
    )

    if np.dtype(encoded_dtype).kind in {'i', 'u'}:
        return np.astype(np.round(y), encoded_dtype)
    else:
        return np.astype(y, encoded_dtype)


def test_lut():
    conversion_gain = 100.0
    zero_level = 0
    beta = 0.5
    input_max = 0x7FFF
    lut = make_anscombe_lookup(
        conversion_gain=conversion_gain,
        input_max=input_max,
        zero_level=zero_level,
        beta=beta,
        output_type="uint8"
    )
    x = np.arange(0, input_max - 1)
    y_lut = lookup(x, lut)
    y_ref = reference_encode(x, conversion_gain, zero_level, beta, "uint8")
    assert np.allclose(y_lut, y_ref, atol=1e-2, rtol=0)