# Quick Start

This guide will help you get started with the Anscombe Transform codec for compressing photon-limited movies.

## Basic Usage with Zarr V3

```python
import zarr
import numpy as np
from anscombe_transform import AnscombeTransformV3

# Synthesize data with Poisson noise - simulating photon-limited microscopy data
n_frames, height, width = 50, 256, 256
mean_photon_rate = 5.0  # Average photons per pixel (exponential distribution of rates)
zero_level = 20.0   # camera baseline
conversion_gain = 30.0  # levels per photon
photon_rate = np.random.exponential(scale=mean_photon_rate, size=(1, height, width))
photon_counts = np.random.poisson(np.tile(photon_rate, (n_frames, 1, 1)))
measured_signal = photon_counts + np.random.randn(*size) * 0.2

data = (zero_level + conversion_gain * measured_signal).astype('int16')

# Create a Zarr array with the Anscombe codec
store = zarr.storage.MemoryStore()
arr = zarr.create(
    store=store,
    shape=data.shape,
    chunks=(12, 160, 80),
    dtype='int16',
    filters=[AnscombeTransformV3(zero_level=zero_level, conversion_gain=conversion_gain)],
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
    shape=data.shape,
    chunks=(12, 160, 80),
    dtype='int16',
    compressor=AnscombeTransformV2(zero_level=zero_level, conversion_gain=conversion_gain)
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
movie = data

# Estimate parameters
result = compute_conversion_gain(data)

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
    shape=data.shape,
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[AnscombeTransformV3(zero_level=zero_level, conversion_gain=conversion_gain)],
    compressor={'id': 'blosc', 'cname': 'zstd', 'clevel': 5},
    zarr_format=3
)
```

## Key Parameters

- **`zero_level`**: The signal value when no photons are detected. This is the baseline offset in your camera sensor.
- **`conversion_gain`** (also called `photon_sensitivity`): How many signal units correspond to one photon. For example, if your camera reports 2.5 levels increase in signal per photon, use `conversion_gain=2.5`.
- **`encoded_dtype`**: The data type for encoded values (default: `uint8`). Use `uint8` for maximum compression.
- **`decoded_dtype`**: The data type for decoded values (default: inferred from data).

## Next Steps

- Learn more in the [User Guide](../user-guide/overview.md)
- See [Parameter Estimation](../user-guide/parameter-estimation.md) for details on computing parameters
- Check out the full [Workbook Example](../examples/workbook.md)
- Explore the [API Reference](../api/codec.md)
