from __future__ import annotations
import numpy as np
from zarr import create_array, open_array
from anscombe_numcodecs import AnscombeCodecV2, AnscombeCodecV3
from tests.conftest import nearly_equal


def test_zarr_v2_roundtrip() -> None:
    decoded_dtype = "int16"
    encoded_dtype = "uint8"
    data = np.random.poisson(100, size=(20, 20)).astype(decoded_dtype)
    sensitivity = 100.0
    codec = AnscombeCodecV2(
        photon_sensitivity=sensitivity,
        zero_level=0,
        encoded_dtype=encoded_dtype,
        decoded_dtype=decoded_dtype,
    )
    data_encoded = codec.encode(data)
    data_rt = codec.decode(data_encoded).reshape(data.shape)

    store = {}

    # write data
    _ = create_array(store=store, data=data, zarr_format=2, compressors=codec)
    # read data
    z_arr_r = open_array(store=store)
    assert z_arr_r.dtype == decoded_dtype
    assert nearly_equal(z_arr_r, data_rt, sensitivity / 2)


def test_zarr_v3_roundtrip() -> None:
    decoded_dtype = "int16"
    encoded_dtype = "uint8"
    data = np.random.poisson(100, size=(20, 20)).astype(decoded_dtype)
    sensitivity = 100.0
    codec = AnscombeCodecV3(
        photon_sensitivity=sensitivity,
        zero_level=0,
        encoded_dtype=encoded_dtype,
        decoded_dtype=decoded_dtype,
    )

    # Test encoding/decoding directly
    data_encoded = codec._encode(data)
    data_rt = codec._decode(data_encoded).reshape(data.shape)

    store = {}

    # write data
    _ = create_array(store=store, data=data, zarr_format=3, filters=[codec])
    # read data
    z_arr_r = open_array(store=store)
    assert z_arr_r.dtype == decoded_dtype
    assert nearly_equal(z_arr_r, data_rt, sensitivity / 2)
