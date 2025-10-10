# Parameter Estimation

To use the Anscombe Transform codec effectively, you need two key parameters:

1. **`zero_level`**: The baseline signal value when no photons are detected
2. **`conversion_gain`** (also called `photon_sensitivity`): The conversion factor from signal units to photon counts

This guide explains how to estimate these parameters from your data.

## The `compute_sensitivity()` Function

The codec provides a built-in parameter estimation function:

```python
from anscombe_transform import compute_sensitivity
import numpy as np

# Load your movie data as (time, height, width)
movie = load_my_movie()  # Shape: (n_frames, height, width)

# Estimate parameters
result = compute_sensitivity(movie)

print(f"Conversion gain: {result['sensitivity']:.3f}")
print(f"Zero level: {result['zero_level']:.3f}")
```

### Input Requirements

The `compute_sensitivity()` function expects:
- **Shape**: `(time, height, width)` - temporal axis must be first
- **Data type**: Integer or float
- **Minimum frames**: At least 10-20 frames for reliable estimation
- **Static scene**: Works best when the scene doesn't change much over time

### How It Works

The function uses the **noise transfer function** approach:

1. **Compute temporal variance**: Calculate pixel-wise variance across time
2. **Compute temporal mean**: Calculate pixel-wise mean across time
3. **Fit noise model**: Use HuberRegressor to fit `variance = slope * mean + intercept`

For Poisson noise: `variance = conversion_gain * (mean - zero_level)`

Therefore:
- `conversion_gain = slope`
- `zero_level = -intercept / slope`

### Return Value

The function returns a dictionary with:

```python
{
    'sensitivity': float,      # The conversion gain (photons per signal unit)
    'zero_level': float,       # The baseline signal level
    'variance': ndarray,       # Computed pixel-wise variance
    'model': HuberRegressor    # The fitted regression model
}
```

## Manual Parameter Estimation

If you know your camera specifications, you can compute the parameters manually:

### Zero Level

The zero level is typically:
- **Dark current**: The signal level with the shutter closed
- **Bias level**: The electronic offset added to prevent negative values

To measure:
1. Capture several frames with no light (shutter closed or lens cap on)
2. Compute the median value across all pixels and frames

```python
dark_frames = capture_dark_frames(n=20)
zero_level = np.median(dark_frames)
```

### Conversion Gain

The conversion gain depends on your camera's specifications:

```python
# If you know electrons per ADU:
electrons_per_adu = 2.5  # From camera spec sheet
quantum_efficiency = 0.9  # Photons to electrons conversion

conversion_gain = electrons_per_adu / quantum_efficiency
```

Or measure from a uniform illumination:

```python
# Capture frames of uniform illumination
uniform_frames = capture_uniform_frames(n=100)

# Compute mean and variance for each pixel
mean = np.mean(uniform_frames, axis=0)
variance = np.var(uniform_frames, axis=0)

# For Poisson noise: variance = gain * (mean - zero)
# Fit a line through the origin after subtracting zero level
conversion_gain = np.median(variance / (mean - zero_level))
```

## Validation

After estimating parameters, validate them:

```python
from anscombe_transform import AnscombeTransformV3

# Create codec with estimated parameters
codec = AnscombeTransformV3(
    zero_level=result['zero_level'],
    conversion_gain=result['sensitivity']
)

# Test on a sample frame
frame = movie[0]
encoded = codec.encode(frame)
decoded = codec.decode(encoded)

# Check reconstruction error
error = np.abs(frame - decoded)
max_error = np.max(error)
mean_error = np.mean(error)

print(f"Max error: {max_error:.2f} ADU")
print(f"Mean error: {mean_error:.2f} ADU")
print(f"Expected noise (1 photon): {result['sensitivity']:.2f} ADU")

# Error should be less than ~1 photon equivalent
assert max_error < 2 * result['sensitivity']
```

## Best Practices

### Data Collection

1. **Use multiple frames**: 20+ frames for reliable statistics
2. **Avoid motion**: Use static scenes or stabilized video
3. **Cover dynamic range**: Include both bright and dark regions
4. **Use raw data**: Don't use pre-processed or normalized data

### Parameter Refinement

1. **Check fit quality**: Inspect `result['model'].score()` (R² should be > 0.95)
2. **Visualize fit**: Plot variance vs. mean to verify linear relationship
3. **Test reconstruction**: Verify that encoding/decoding preserves data quality

### Common Issues

**Negative zero level**: Usually indicates pre-processed data or incorrect bias subtraction. Check if your data has been normalized.

**Very high conversion gain (> 10)**: May indicate the data is already in photon units or has been scaled.

**Poor R² score (< 0.9)**: Could mean:
- Too much motion in the scene
- Non-Poisson noise dominates (e.g., readout noise)
- Not enough temporal variation

## Example Workflow

```python
import numpy as np
from anscombe_transform import compute_sensitivity, AnscombeTransformV3
import zarr

# 1. Load temporal data
movie = load_movie()  # Shape: (100, 512, 512)

# 2. Estimate parameters
params = compute_sensitivity(movie)
print(f"Estimated parameters:")
print(f"  Conversion gain: {params['sensitivity']:.3f} ADU/photon")
print(f"  Zero level: {params['zero_level']:.1f} ADU")

# 3. Validate fit quality
r2_score = params['model'].score(
    params['variance'].ravel().reshape(-1, 1),
    np.mean(movie, axis=0).ravel()
)
print(f"  Fit quality (R²): {r2_score:.3f}")

# 4. Create codec with estimated parameters
codec = AnscombeTransformV3(
    zero_level=params['zero_level'],
    conversion_gain=params['sensitivity']
)

# 5. Create Zarr array
arr = zarr.create(
    shape=movie.shape,
    chunks=(10, 512, 512),
    dtype='int16',
    filters=[codec],
    zarr_format=3
)

# 6. Compress data
arr[:] = movie
print(f"Compression successful!")
```

## Next Steps

- [Zarr V2 Integration](zarr-v2.md)
- [Zarr V3 Integration](zarr-v3.md)
- [API Reference: estimate module](../api/estimate.md)
