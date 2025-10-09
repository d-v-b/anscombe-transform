# `anscombe-transform` Codec

This specification defines an array-array codec that encodes an input array using the [Anscombe transform](https://en.wikipedia.org/wiki/Anscombe_transform) followed by an optional data type casting operations and decodes using the inverted type cast and the inverse Anscombe transform. This transformation is not generally lossless, but is useful as for conditioning data prior to compression.

## Anscombe transform

The Anscombe transform is [bijection](https://en.wikipedia.org/wiki/Bijection) from a [Poisson-distributed](https://en.wikipedia.org/wiki/Poisson_distribution) variable to an approximately [Gaussian-distributed](https://en.wikipedia.org/wiki/Normal_distribution) variable with a variance of 1.

This transformation is useful in sensing applications to mitigate [shot noise](https://en.wikipedia.org/wiki/Shot_noise). Shot noise is typically modelled as a Poisson process. The variance of a Poisson-distributed signal scales with its mean. The Anscombe transform maps a Poisson-distributed signal to a Gaussian-distributed signal with a variance near 1. Decoupling the mean of the signal from its variance facilitates noise removal and data compression, the latter of which is the intended application of this codec.

## Codec algorithm

### Encoding

In addition to the input array, the encoding procedure takes the following parameters:

| name | type | 
| - | - | 
| `conversion_gain` | positive real number |
| `zero_level` | real number |
| `beta` | real number from the inverval `(0, 1]` |
| `encoded_dtype` | Zarr V3 data type | 

For each element `x` of the input array, an output value `y` is generated via the following procedure:

```python
import math
def anscombe_transform(x, conversion_gain, zero_level, beta, encoded_dtype):
    # Convert to event units
    event_rate = (x - zero_level) / conversion_gain

    zero_slope = 1.0 / (beta * math.sqrt(3.0 / 8.0))
    offset = zero_level * zero_slope / conversion_gain

    if value < 0:
        # Linear extrapolation
        result = offset + value * zero_slope
    else:
        # Anscombe transform
        result = offset + (2.0 / beta) * (math.sqrt(value + 3.0 / 8.0) - math.sqrt(3.0 / 8.0))
    
    # This assumes the existence of a cast_dtype procedure 
    return cast_dtype(result, encoded_dtype)

```
### Decoding

In addition to the input array, the decoding procedure takes the following parameters:

| name | type | 
| - | - | 
| `conversion_gain` | positive real number |
| `zero_level` | real number |
| `beta` | real number from the inverval `(0, 1]` |
| `encoded_dtype` | Zarr V3 data type | 

## Codec metadata

| field | type | required | notes |
| - | - | - | - |
| `"name"` | literal `"anscombe-transform"` | yes | |
| `"configuration"` | [anscombe transform configuration](#configuration-metadata) | yes | |

#### Configuration metadata

| field | type | required | notes |
| - | - | - | - |
| `"zero_level"` | number | yes | The value in the input array that corresponds to 0 detected events.
| `"beta"` | number from the interval `(0, 1]` | yes | <TODO> |
| `"conversion_gain"` | positive number | yes | The magnitude of a single recorded event in the input data |
| `"decoded_dtype"` | Zarr V3 data type metadata| yes | The data type of the *input array*. |
| `"encoded_dtype"` | Zarr V3 data type metadata| yes | The data type of the output array. |  

### Supported array data types

This codec is compatible with any array data type that supports the operations required to implement the Anscombe transformation and its inverse. 
