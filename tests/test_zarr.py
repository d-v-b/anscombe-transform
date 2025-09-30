from __future__ import annotations
import pytest
import numpy as np
from zarr import create_array, open_array
from anscombe_numcodecs import AnscombeCodecV2, encode, decode

def test_zarr_v2_roundtrip() -> None:
    data = np.random.poisson(100, size=(20, 20)).astype('uint8')
    sensitivity = 100.0
    codec = AnscombeCodecV2(
        photon_sensitivity=sensitivity,
        zero_level=0,
        encoded_dtype='uint8',
        decoded_dtype='int16')
    data_encoded = codec.encode(
        data)
    data_rt = codec.decode(
        data_encoded)

    store = {}

    # write data
    z_arr_w = create_array(
        store=store, 
        data=data, 
        zarr_format=2, 
        compressors=codec)

    # read data
    z_arr_r = open_array(store=store)
    assert z_arr_r[:] == data_rt