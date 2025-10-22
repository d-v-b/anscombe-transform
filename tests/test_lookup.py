from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from zarr.core.dtype import ZDType
import numpy as np
from zarr.core.dtype import UInt8

from anscombe_transform.codec import lookup, make_anscombe_lookup

def reference_encode(
        x: np.ndarray, 
        conversion_gain: float, 
        zero_level: float, 
        beta: float, 
        encoded_dtype: ZDType[Any, Any]):
    """
    A reference implementation of the encoding step of the Anscombe transform codec.

    Parameters
    ----------
    x : array_like or float
        Input value(s)
    conversion_gain : float
        The size of one photon in the input units (e.g. counts per photon).
    zero_level : float
        The baseline offset of the sensor (default 0).
    beta : float
        Output scaling factor in units of noise std dev.
        Must be > 0. (Default: 0.5)

    Returns
    -------
    y : ndarray or float
        Variance-stabilized output values.
    """

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
    # Convert Zarr dtype to native dtype (numpy)
    np_dtype = encoded_dtype.to_native_dtype()
    if np_dtype.kind in {'i', 'u'}:
        return np.astype(np.round(y), np_dtype)
    else:
        return np.astype(y, np_dtype)

def reference_decode(
        x: np.ndarray,
        conversion_gain: float,
        zero_level: float,
        beta: float,
        decoded_dtype: ZDType[Any, Any]):
    """
    A reference implementation of the decoding step of the Anscombe transform codec.

    Parameters
    ----------
    x : array_like or float
        Encoded input value(s) from the Anscombe transform.
    conversion_gain : float
        The size of one photon in the input units (e.g. counts per photon).
    zero_level : float, optional
        The baseline offset of the sensor (default 0).
    beta : float, optional
        Output scaling factor in units of noise std dev.
        Must be > 0. (Default: 0.5)
    decoded_dtype : ZDType
        The output dtype for the decoded values.

    Returns
    -------
    y : ndarray or float
        Decoded output values in original domain.
    """
    # Precompute constants (same as encoding)
    zero_slope = 1.0 / (beta * np.sqrt(3.0 / 8.0))
    offset = zero_level * zero_slope / conversion_gain

    x_arr = np.asarray(x, dtype=float)

    # Determine which values were in the linear region (negative x_events)
    # and which were in the sqrt region (positive x_events)
    # The threshold in transformed space is at offset (when x_events = 0)

    # For the linear region: y = offset + x_events * zero_slope
    # Solving for x_events: x_events = (y - offset) / zero_slope
    x_events_linear = (x_arr - offset) / zero_slope

    # For the sqrt region: y = offset + (2.0 / beta) * (sqrt(x_events + 3/8) - sqrt(3/8))
    # Solving for x_events:
    # y - offset = (2.0 / beta) * (sqrt(x_events + 3/8) - sqrt(3/8))
    # (y - offset) * beta / 2.0 = sqrt(x_events + 3/8) - sqrt(3/8)
    # sqrt(x_events + 3/8) = (y - offset) * beta / 2.0 + sqrt(3/8)
    # x_events + 3/8 = ((y - offset) * beta / 2.0 + sqrt(3/8))^2
    # x_events = ((y - offset) * beta / 2.0 + sqrt(3/8))^2 - 3/8

    sqrt_term = (x_arr - offset) * beta / 2.0 + np.sqrt(3.0 / 8.0)
    x_events_sqrt = sqrt_term ** 2 - 3.0 / 8.0

    # Use linear inversion for values at or below the threshold (offset)
    # and sqrt inversion for values above
    x_events = np.where(x_arr <= offset, x_events_linear, x_events_sqrt)

    # Convert events back to original values
    y = x_events * conversion_gain + zero_level

    # Convert to native dtype with clipping to valid range
    np_dtype = decoded_dtype.to_native_dtype()
    if np_dtype.kind in {'i', 'u'}:
        # Clip to valid range for integer types to avoid overflow
        info = np.iinfo(np_dtype)
        y_clipped = np.clip(y, info.min, info.max)
        return np.asarray(np.round(y_clipped), np_dtype)
    else:
        return np.asarray(y, np_dtype)


def test_reference_encode():
    """
    Test the efficient, lookup table-based encoding procedure 
    agains the slower reference implementation.
    """
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
    y_ref = reference_encode(x, conversion_gain, zero_level, beta, UInt8())
    assert np.allclose(y_lut, y_ref, atol=1e-2, rtol=0)

def test_reference_decode():
    """
    Test the efficient, lookup table-based decoding procedure
    against the slower reference implementation.
    """
    conversion_gain = 100.0
    zero_level = 0
    beta = 0.5
    input_max = 0x7FFF

    # Create forward lookup table
    forward_lut = make_anscombe_lookup(
        conversion_gain=conversion_gain,
        input_max=input_max,
        zero_level=zero_level,
        beta=beta,
        output_type="uint8"
    )

    # Create inverse lookup table
    from anscombe_transform.codec import make_inverse_lookup
    inverse_lut = make_inverse_lookup(forward_lut, output_type="int16")

    # Test with encoded values (the range of the forward lookup table)
    # Exclude edge cases at 0 and max where the midpoint and mathematical inverse differ most
    x = np.arange(1, forward_lut.max(), dtype="uint8")

    # Apply lookup-based decoding
    y_lut = lookup(x, inverse_lut)

    # Apply reference decoding
    from zarr.core.dtype import Int16
    y_ref = reference_decode(x, conversion_gain, zero_level, beta, Int16())

    # The LUT uses midpoints of ranges while the reference uses mathematical inverse
    # They should be close but not exact due to rounding and the midpoint approximation
    assert np.allclose(y_lut, y_ref, atol=5, rtol=0.01)
