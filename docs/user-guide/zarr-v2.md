# Zarr V2 Integration

This guide covers using the Anscombe Transform codec with Zarr V2.

## Basic Usage

```python
import zarr
import numpy as np
from anscombe_transform import AnscombeTransformV2

# Create data
data = np.random.poisson(lam=50, size=(100, 512, 512)).astype('int16')

# Create Zarr V2 array with Anscombe codec as compressor
arr = zarr.open_array(
    'data.zarr',
    mode='w',
    shape=data.shape,
    chunks=(10, 512, 512),
    dtype='int16',
    compressor=AnscombeTransformV2(
        zero_level=100,
        conversion_gain=2.5
    )
)

# Write and read
arr[:] = data
recovered = arr[:]
```

## Using with Additional Compression

In Zarr V2, the Anscombe codec can be combined with other compressors by nesting them:

```python
from numcodecs import Blosc
from anscombe_transform import AnscombeTransformV2

# Note: Zarr V2 doesn't support filter chains natively
# The Anscombe codec must be the primary compressor
compressor = AnscombeTransformV2(
    zero_level=100,
    conversion_gain=2.5,
    encoded_dtype='uint8'
)

arr = zarr.open_array(
    'compressed.zarr',
    mode='w',
    shape=(100, 512, 512),
    chunks=(10, 512, 512),
    dtype='int16',
    compressor=compressor
)
```

!!! note "Limitation"
    Zarr V2 doesn't support filter chains like V3 does. The Anscombe codec serves as both the transform and the compressor. For better compression with additional algorithms, consider upgrading to Zarr V3.

## Codec Parameters

### Required Parameters

- **`zero_level`** (float): Baseline signal with no photons
- **`conversion_gain`** (float): Signal units per photon (also called `photon_sensitivity`)

### Optional Parameters

- **`encoded_dtype`** (str or dtype): Data type for encoded values, default: `'uint8'`
  - Use `'uint8'` for maximum compression (0-255 range)
  - Use `'uint16'` for higher dynamic range
- **`decoded_dtype`** (str or dtype): Data type for decoded output, default: inferred from input

## Codec Registration

The codec is automatically registered when you import it:

```python
from anscombe_transform import AnscombeTransformV2
import numcodecs

# The codec is now registered
codec = numcodecs.get_codec({'id': 'anscombe-v1', 'zero_level': 100, 'conversion_gain': 2.5})
```

## Serialization

The codec can be serialized to/from JSON:

```python
from anscombe_transform import AnscombeTransformV2

# Create codec
codec = AnscombeTransformV2(zero_level=100, conversion_gain=2.5)

# Serialize to dict
config = codec.get_config()
print(config)
# {'id': 'anscombe-v1', 'zero_level': 100, 'conversion_gain': 2.5, ...}

# Deserialize from dict
codec2 = AnscombeTransformV2.from_config(config)
```

This is useful for:
- Storing codec configuration in metadata
- Sharing compression settings across systems
- Programmatic codec creation

## Working with Existing Arrays

### Reading Compressed Data

If data was compressed with the Anscombe codec:

```python
import zarr
from anscombe_transform import AnscombeTransformV2

# Open existing array (codec info is stored in .zarray metadata)
arr = zarr.open_array('data.zarr', mode='r')

# Read data (automatically decompressed)
data = arr[:]
```

### Inspecting Codec Configuration

```python
import zarr
import json

# Read .zarray metadata
with open('data.zarr/.zarray', 'r') as f:
    metadata = json.load(f)

print(metadata['compressor'])
# {'id': 'anscombe-v1', 'zero_level': 100, 'conversion_gain': 2.5, ...}
```

## Migration to Zarr V3

To migrate data from V2 to V3:

```python
import zarr
from anscombe_transform import AnscombeTransformV2, AnscombeTransformV3

# Open V2 array
v2_arr = zarr.open_array('data_v2.zarr', mode='r')

# Get codec config
v2_config = v2_arr.compressor.get_config()

# Create V3 array with equivalent codec
v3_arr = zarr.create(
    shape=v2_arr.shape,
    chunks=v2_arr.chunks,
    dtype=v2_arr.dtype,
    filters=[AnscombeTransformV3(
        zero_level=v2_config['zero_level'],
        conversion_gain=v2_config['conversion_gain']
    )],
    zarr_format=3
)

# Copy data
v3_arr[:] = v2_arr[:]
```

## API Reference

See the [Codec API Reference](../api/codec.md) for detailed documentation of all parameters and methods.

## Next Steps

- [Zarr V3 Integration](zarr-v3.md) - Learn about the improved V3 interface
- [Parameter Estimation](parameter-estimation.md) - Estimate codec parameters from data
- [Examples](../examples/workbook.md) - See complete examples
