# Zarr V3 Integration

This guide covers using the Anscombe Transform codec with Zarr V3, which provides improved performance and flexibility.

## Basic Usage

```python
import zarr
import numpy as np
from anscombe_transform import AnscombeTransformV3

# Create data
data = np.random.poisson(lam=50, size=(100, 512, 512)).astype('int16')

# Create Zarr V3 array with Anscombe codec as a filter
store = zarr.storage.MemoryStore()
arr = zarr.create(
    store=store,
    shape=data.shape,
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[AnscombeTransformV3(
        zero_level=100,
        conversion_gain=2.5
    )],
    zarr_format=3
)

# Write and read
arr[:] = data
recovered = arr[:]
```

## Filter Chains

Zarr V3 supports filter chains, allowing you to combine the Anscombe transform with other compression algorithms:

```python
import zarr
from anscombe_transform import AnscombeTransformV3

# Use Anscombe as a filter with Blosc compression
arr = zarr.create(
    shape=(100, 512, 512),
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[
        AnscombeTransformV3(zero_level=100, conversion_gain=2.5)
    ],
    compressor={
        'id': 'blosc',
        'cname': 'zstd',
        'clevel': 5,
        'shuffle': 'bitshuffle'
    },
    zarr_format=3
)
```

The processing pipeline is:
1. **Original data** (int16)
2. **Anscombe filter** → transformed data (uint8)
3. **Blosc compressor** → compressed bytes
4. **Storage**

## Recommended Compressors

Different compressors work well with the Anscombe-transformed data:

### Blosc with Zstd (Best Overall)

```python
filters = [AnscombeTransformV3(zero_level=100, conversion_gain=2.5)]
compressor = {
    'id': 'blosc',
    'cname': 'zstd',      # Excellent compression + speed
    'clevel': 5,          # Compression level (1-9)
    'shuffle': 'bitshuffle'
}
```

### Blosc with LZ4 (Fastest)

```python
compressor = {
    'id': 'blosc',
    'cname': 'lz4',       # Fastest decompression
    'clevel': 3,
    'shuffle': 'bitshuffle'
}
```

### Blosc with Zlib (Maximum Compression)

```python
compressor = {
    'id': 'blosc',
    'cname': 'zlib',      # Best compression ratio
    'clevel': 9,
    'shuffle': 'bitshuffle'
}
```

## Codec Parameters

### Required Parameters

- **`zero_level`** (float): Baseline signal with no photons
- **`conversion_gain`** (float): Signal units per photon

### Optional Parameters

- **`encoded_dtype`** (str or dtype): Data type for encoded values, default: `'uint8'`
- **`decoded_dtype`** (str or dtype): Data type for decoded output, default: inferred
- **`beta`** (float): Quantization step size in noise standard deviations, default: `0.5`

### Advanced: Beta Parameter

The `beta` parameter controls the quantization precision:

```python
# Finer quantization (more levels, better accuracy, less compression)
codec_fine = AnscombeTransformV3(
    zero_level=100,
    conversion_gain=2.5,
    beta=0.25  # Half the default step size
)

# Coarser quantization (fewer levels, more compression, lower accuracy)
codec_coarse = AnscombeTransformV3(
    zero_level=100,
    conversion_gain=2.5,
    beta=1.0  # Double the default step size
)
```

Default `beta=0.5` means each quantization level represents 0.5 standard deviations of noise, which is a good balance for most applications.

## Codec Registration

The codec is automatically registered with Zarr V3:

```python
from anscombe_transform import AnscombeTransformV3
import zarr

# Check if registered
print('anscombe-v1' in zarr.codecs.registry.get_codec_class('anscombe-v1'))
```

## Serialization and Metadata

### Codec Configuration

The codec configuration is stored in the array metadata:

```python
import zarr
from anscombe_transform import AnscombeTransformV3

# Create array
arr = zarr.create(
    shape=(100, 512, 512),
    dtype='int16',
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    zarr_format=3
)

# Access metadata
print(arr.metadata)
```

### JSON Serialization

```python
from anscombe_transform import AnscombeTransformV3

codec = AnscombeTransformV3(zero_level=100, conversion_gain=2.5)

# Convert to dict
config = codec.to_dict()
print(config)
# {'name': 'anscombe-v1', 'configuration': {'zero_level': 100, ...}}

# Reconstruct from dict
codec2 = AnscombeTransformV3.from_dict(config)
```

## Performance Optimization

### Chunk Size Selection

Choose chunk sizes that balance compression and access patterns:

```python
# For sequential access (e.g., video playback)
chunks = (10, 512, 512)  # 10 frames at a time

# For random time-point access
chunks = (1, 512, 512)   # Single frames

# For spatial crops across time
chunks = (100, 128, 128) # Smaller spatial regions, all time points
```

### Parallel Processing

Zarr V3 supports parallel chunk processing:

```python
import zarr
from concurrent.futures import ThreadPoolExecutor

arr = zarr.open_array('data.zarr', mode='r')

# Read chunks in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for i in range(0, arr.shape[0], 10):
        future = executor.submit(lambda i=i: arr[i:i+10])
        futures.append(future)

    results = [f.result() for f in futures]
```

## Working with Different Storage Backends

### Local Filesystem

```python
import zarr
from anscombe_transform import AnscombeTransformV3

store = zarr.storage.LocalStore('data.zarr')
arr = zarr.create(
    store=store,
    shape=(100, 512, 512),
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    zarr_format=3
)
```

### In-Memory

```python
store = zarr.storage.MemoryStore()
arr = zarr.create(
    store=store,
    shape=(100, 512, 512),
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    zarr_format=3
)
```

### Remote Storage (S3, GCS)

```python
import zarr
from anscombe_transform import AnscombeTransformV3

# Requires fsspec and s3fs/gcsfs
store = zarr.storage.RemoteStore('s3://bucket/data.zarr')
arr = zarr.create(
    store=store,
    shape=(100, 512, 512),
    filters=[AnscombeTransformV3(zero_level=100, conversion_gain=2.5)],
    zarr_format=3
)
```

## API Reference

See the [Codec API Reference](../api/codec.md) for detailed documentation.

## Next Steps

- [Parameter Estimation](parameter-estimation.md) - Estimate codec parameters
- [Examples](../examples/workbook.md) - Complete workflow examples
- [Zarr V2 Integration](zarr-v2.md) - If you need V2 compatibility
