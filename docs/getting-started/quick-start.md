# Quick Start

This guide will help you get started with the Anscombe Transform codec for compressing photon-limited movies.

## Basic Usage with Zarr V3

```python
import zarr
import numpy as np
from anscombe_transform import AnscombeTransformV3

# Generate sample data with Poisson noise
# Simulating photon-limited imaging data
data = np.random.poisson(lam=50, size=(100, 512, 512)).astype('int16')

# Create a Zarr array with the Anscombe codec
store = zarr.storage.MemoryStore()
arr = zarr.create(
    store=store,
    shape=data.shape,
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    zarr_format=3
)

# Write data
arr[:] = data

# Read data back
recovered = arr[:]

# Verify roundtrip accuracy
print(f"Max difference: {np.abs(data - recovered).max()}")
```

## Using with Zarr V2

```python
from anscombe_transform import AnscombeTransformV2
import zarr

# Create array with V2 codec
arr = zarr.open_array(
    'data.zarr',
    mode='w',
    shape=(100, 512, 512),
    chunks=(10, 512, 512),
    dtype='int16',
    compressor=AnscombeTransformV2(zero_level=100, conversion_gain=2.5)
)

# Write and read data
arr[:] = data
recovered = arr[:]
```

## Estimating Parameters from Data

If you don't know the `zero_level` and `conversion_gain` parameters, you can estimate them from your data:

```python
from anscombe_transform import compute_conversion_gain
import numpy as np

# Load your movie data as (time, height, width)
movie = np.random.poisson(lam=50, size=(100, 512, 512))

# Estimate parameters
result = compute_conversion_gain(movie)

print(f"Estimated conversion gain: {result['sensitivity']:.3f}")
print(f"Estimated zero level: {result['zero_level']:.3f}")

# Use estimated parameters in codec
codec = AnscombeTransformV3(
    zero_level=result['zero_level'],
    conversion_gain=result['sensitivity']
)
```

## Combining with Other Compressors

The Anscombe codec is typically used as a filter before compression:

```python
import zarr
from numcodecs import Blosc
from anscombe_transform import AnscombeTransformV3

# For Zarr V3, use filters + codecs
arr = zarr.create(
    shape=(100, 512, 512),
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    compressor={'id': 'blosc', 'cname': 'zstd', 'clevel': 5},
    zarr_format=3
)
```

## Key Parameters

- **`zero_level`**: The signal value when no photons are detected. This is the baseline offset in your camera sensor.
- **`conversion_gain`** (also called `photon_sensitivity`): How many signal units correspond to one photon. For example, if your camera reports 2.5 ADU per photon, use `conversion_gain=2.5`.
- **`encoded_dtype`**: The data type for encoded values (default: `uint8`). Use `uint8` for maximum compression.
- **`decoded_dtype`**: The data type for decoded values (default: inferred from data).

## Next Steps

- Learn more in the [User Guide](../user-guide/overview.md)
- See [Parameter Estimation](../user-guide/parameter-estimation.md) for details on computing parameters
- Check out the full [Workbook Example](../examples/workbook.md)
- Explore the [API Reference](../api/codec.md)
