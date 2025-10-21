# `anscombe-transform` Codec

This specification defines an [array->array codec](https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html#id22) that encodes an input array using the [Anscombe transform](https://en.wikipedia.org/wiki/Anscombe_transform) followed by an optional data type casting operations and decodes using the inverted type cast and the inverse Anscombe transform. This transformation is not generally lossless, but is useful as for conditioning data prior to compression.

## Anscombe transform

The Anscombe transform is [bijection](https://en.wikipedia.org/wiki/Bijection) from a [Poisson-distributed](https://en.wikipedia.org/wiki/Poisson_distribution) variable to an approximately [Gaussian-distributed](https://en.wikipedia.org/wiki/Normal_distribution) variable with a variance of 1.

This transformation is useful in sensing applications to mitigate [shot noise](https://en.wikipedia.org/wiki/Shot_noise). Shot noise is typically modelled as a Poisson process. The variance of a Poisson-distributed signal scales with its mean. The Anscombe transform maps a Poisson-distributed signal to a Gaussian-distributed signal with a variance near 1. Decoupling the mean of the signal from its variance facilitates noise removal and data compression, the latter of which is the intended application of this codec.

## Codec algorithm

### Encoding

#### Parameters

In addition to the input array, the encoding procedure takes the following parameters:

| name | type | 
| - | - | 
| `conversion_gain` | positive real number |
| `zero_level` | real number |
| `beta` | positive real number | ratio of quantization step / noise
| `encoded_dtype` | Zarr V3 data type | 

#### Algorithm

For each element $x$ of the input array, an output value $y$ is generated via the following procedure:


1. $x$ is normalized by subtracting $\text{zero\_level}$ and then dividing by $\text{conversion\_gain}$. The result of this transformation, called $x_{\text{norm}}$, now represents a quantity of observed events. 
    
    Schematically:

    $x_{\text{norm}} := \frac{x - \text{zero\_level}}{\text{conversion\_gain}}$

2. If $x_{\text{norm}}$ is non-negative, we apply the Anscombe transform, multiply by a scaling factor, and add an offset, and bind $\text{result}$ to the result. Schematically, the transformation is as follows:

$$
\text{result} := \frac{1}{\text{beta}} \left(\frac{\text{zero\_level}}{\text{conversion\_gain} \, *  \sqrt{3/8}}
+ 2 \left( \sqrt{x_{\text{norm}} + \tfrac{3}{8}} - \sqrt{\tfrac{3}{8}} \right)\right)
$$

The additional scaling and offset factors ensure that the transform maps the $\text{zero\_level}$ value to $0$, and also that the transform is continuous around 0, because we will use linear extrapolation to resolve negative values of $x_{\text{norm}}$.

When $x_{\text{norm}}$ is negative, we bind $\text{result}$ to $x$ divided by the product of $\text{beta}$ , $\text{conversion\_gain}$, and $\sqrt{3/8}$. This is effectively linear extrapolation from 0 in the negative direction. Schematically:

$$
\text{result} :=      \frac
        {x}
        {\text{beta} * \text{conversion\_gain} *\sqrt{3/8} } 
$$

If `encoded_dtype` denotes an integer data type, then $\text{result}$ is rounded before the data type casting procedure.

#### Reference python function

The above procedure is implemented in the following reference Python function:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["zarr>=3.1.1", "numpy==2.2"]
# ///
import numpy as np
from zarr.core.dtype import ZDType
def anscombe_transform(x, conversion_gain: float, zero_level: float, beta: float, encoded_dtype: ZDType):
    # Convert to event units
    event_rate = (x - zero_level) / conversion_gain

    zero_slope = 1.0 / (beta * np.sqrt(3.0 / 8.0))
    offset = zero_level * zero_slope / conversion_gain

    if event_rate < 0:
        # Linear extrapolation
        result = offset + event_rate * zero_slope
    else:
        # Anscombe transform
        result = offset + (2.0 / beta) * (np.sqrt(event_rate + 3.0 / 8.0) - np.sqrt(3.0 / 8.0))
    
    # When converting from a floating point to an integer data type,
    # values should be rounded prior to type conversion
    np_dtype = encoded_dtype.to_native_dtype()
    if np_dtype.kind in {"i", "u"}:
        return np.astype(np.round(result), np_dtype)
    return np.astype(result, np_dtype)
```
### Decoding

#### Algorithm

To decode Anscombe-transformed data, invert the [encoding algorithm](#algorithm). Depending on the choice of output data type, the decoded data may not match exactly the input.

#### Parameters

In addition to the input array, the decoding procedure takes the following parameters:

| name | type | 
| - | - | 
| `conversion_gain` | positive real number |
| `zero_level` | real number |
| `beta` | positive real number |
| `decoded_dtype` | Zarr V3 data type | 

These are the same as the parameters used for the [encoding procedure](#parameters) minus the `encoded_dtype`; the `decoded_dtype` is required instead.

## Codec metadata

| field | type | required | notes |
| - | - | - | - |
| `name` | literal `"anscombe-transform"` | yes | |
| `configuration` | [anscombe transform configuration](#configuration-metadata) | yes | |

#### Configuration metadata

| field | type | required | notes |
| - | - | - | - |
| `zero_level` | number | yes | The value in the input array that corresponds to 0 detected events.
| `beta` | positive number | yes | Ratio of quantization step to noise. Typical values are between 0.5 and 2.  |
| `conversion_gain` | positive number | yes | The magnitude of a single recorded event in the input data |
| `decoded_dtype` | Zarr V3 data type metadata| yes | The Zarr data type of the *input array*. |
| `encoded_dtype` | Zarr V3 data type metadata| yes | The Zarr data type of the output array. |  

### Supported array data types

This codec is compatible with array data types that model real numbers or a subset thereof. 
