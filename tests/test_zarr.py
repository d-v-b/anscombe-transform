from __future__ import annotations

import numpy as np
from zarr import create_array, open_array

from anscombe_transform import AnscombeTransformV2, AnscombeTransformV3
from tests.conftest import nearly_equal


def test_zarr_v2_roundtrip() -> None:
    decoded_dtype = "int16"
    encoded_dtype = "uint8"

    # generate fake data
    np.random.seed(42)
    size = (20, 20)
    sensitivity = 100.0
    zero_level = -5.0
    true_rate = np.random.exponential(scale=5, size=size)
    data = (
        zero_level
        + sensitivity * (np.random.poisson(true_rate) + np.random.randn(*size) * 0.25)
    ).astype(decoded_dtype)

    # construct codec
    codec = AnscombeTransformV2(
        conversion_gain=sensitivity,
        zero_level=zero_level,
        encoded_dtype=encoded_dtype,
        decoded_dtype=decoded_dtype,
    )
    data_encoded = codec.encode(data)
    data_rt = codec.decode(data_encoded).reshape(data.shape)

    # write data
    store = {}
    _ = create_array(store=store, data=data, zarr_format=2, compressors=codec)

    # read data
    z_arr_r = open_array(store=store)
    assert z_arr_r.dtype == decoded_dtype
    assert nearly_equal(z_arr_r, data_rt, sensitivity * 0.5)


def test_zarr_v3_roundtrip() -> None:
    decoded_dtype = "int16"
    encoded_dtype = "uint8"

    # generate fake data
    np.random.seed(42)
    size = (20, 20)
    sensitivity = 100.0
    zero_level = -5.0
    true_rate = np.random.exponential(scale=5, size=size)
    data = (
        zero_level
        + sensitivity * (np.random.poisson(true_rate) + np.random.randn(*size) * 0.25)
    ).astype(decoded_dtype)

    codec = AnscombeTransformV3(
        conversion_gain=sensitivity,
        zero_level=zero_level,
        encoded_dtype=encoded_dtype,
        decoded_dtype=decoded_dtype,
    )

    # Test encoding/decoding directly
    data_encoded = codec._encode(data)
    data_rt = codec._decode(data_encoded).reshape(data.shape)

    # write data
    store = {}
    _ = create_array(store=store, data=data, zarr_format=3, filters=[codec])
    # read data
    z_arr_r = open_array(store=store)
    assert z_arr_r.dtype == decoded_dtype
    assert nearly_equal(z_arr_r, data_rt, sensitivity / 2)
