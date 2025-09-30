from __future__ import annotations
import pytest
import numpy as np
from zarr import create_array, open_array
from anscombe_numcodecs import AnscombeCodecV2, encode, decode
from tests.conftest import nearly_equal

def test_zarr_v2_roundtrip() -> None:
    data = np.random.poisson(100, size=(20, 20)).astype('uint8')
    encoded_dtype = 'uint8'
    decoded_dtype = 'int16'
    sensitivity = 100.0
    codec = AnscombeCodecV2(
        photon_sensitivity=sensitivity,
        zero_level=0,
        encoded_dtype=encoded_dtype,
        decoded_dtype=decoded_dtype)
    data_encoded = codec.encode(
        data)
    data_rt = codec.decode(
        data_encoded).reshape(data.shape)

    store = {}

    # write data
    z_arr_w = create_array(
        store=store,
        shape=data.shape,
        dtype=decoded_dtype,
        zarr_format=2, 
        compressors=codec)
    z_arr_w[:] = data
    # read data
    z_arr_r = open_array(store=store)
    assert nearly_equal(z_arr_r, data, sensitivity/2)