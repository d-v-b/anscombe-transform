"""
Numcodecs Codec implementation for Anscombe Transform for photon-limited data.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import ClassVar, Literal, Self
import numpy as np
import numcodecs
import numpy.typing as npt
from typing import TypedDict
from zarr.abc.codec import ArrayArrayCodec
from zarr.core.array_spec import ArraySpec
from zarr.core.dtype import parse_dtype


class AnscombeCodecConfig(TypedDict):
    zero_level: int
    photon_sensitivity: float


class AnscomeCodecJSON_V2(AnscombeCodecConfig):
    id: Literal["anscombe-v1"]


# TODO: expose these parameters in the configuration for the codec
def make_anscombe_lookup(
    sensitivity: float,
    input_max: int = 0x7FFF,
    zero_level: int = 0,
    beta: float = 0.5,
    output_type: str = "uint8",
) -> np.ndarray:
    """
    Compute the Anscombe lookup table.
    The lookup converts a linear grayscale image into a uniform variance image.
    :param sensitivity: the size of one photon in the linear input image.
    :param input_max: the maximum value in the input
    :param beta: the grayscale quantization step expressed in units of noise std dev
    """
    xx = (
        np.r_[: input_max + 1] - zero_level
    ) / sensitivity  # input expressed in photon rates
    zero_slope = 1 / beta / np.sqrt(3 / 8)  # slope for negative values
    offset = zero_level * zero_slope / sensitivity
    lookup_table = np.round(
        offset
        + (xx < 0) * (xx * zero_slope)
        + (xx >= 0)
        * (2.0 / beta * (np.sqrt(np.maximum(0, xx) + 3 / 8) - np.sqrt(3 / 8)))
    )
    lookup = lookup_table.astype(output_type)
    assert np.diff(lookup_table).min() >= 0, "non-monotonic lookup generated"
    return lookup


def make_inverse_lookup(lookup_table: np.ndarray, output_type="int16") -> np.ndarray:
    """Compute the inverse lookup table for a monotonic forward lookup table."""
    _, inv1 = np.unique(lookup_table, return_index=True)  # first entry
    _, inv2 = np.unique(lookup_table[::-1], return_index=True)  # last entry
    inverse = (inv1 + lookup_table.size - 1 - inv2) / 2
    return inverse.astype(output_type)


def lookup(movie: np.ndarray, lookup_table: np.ndarray) -> np.ndarray:
    """Apply lookup table to movie"""
    return lookup_table[np.maximum(0, np.minimum(movie, lookup_table.size - 1))]


def encode(
    buf: np.ndarray, *, sensitivity: float, zero_level: int, encoded_dtype: str
) -> np.ndarray:
    """
    Encode an array into a buffer of bytes.
    """
    lut = make_anscombe_lookup(
        sensitivity,
        output_type=encoded_dtype,
        zero_level=zero_level,
    )
    encoded = lookup(buf, lut)
    return encoded.astype(encoded_dtype)


def decode(
    buf: bytes | np.ndarray,
    *,
    sensitivity: float,
    zero_level: int,
    encoded_dtype: npt.DtypeLike,
    decoded_dtype: npt.DTypeLike,
) -> np.ndarray:
    """
    Decode an array from a buffer of bytes.
    """
    lookup_table = make_anscombe_lookup(
        sensitivity,
        output_type=encoded_dtype,
        zero_level=zero_level,
    )
    inverse_table = make_inverse_lookup(lookup_table, output_type=decoded_dtype)
    decoded = np.frombuffer(buf, dtype=encoded_dtype)
    return lookup(decoded, inverse_table).astype(decoded_dtype)


@dataclass(frozen=True, slots=True)
class AnscombeCodecV2:
    """Codec for 3-dimensional Filter. The codec assumes that input data are of shape:
    (time, x, y).

    Parameters
    ----------
    zero_level : float
        Signal level when no photons are recorded.
        This should pre-computed or measured directly on the instrument.
    photon_sensitivity : float
        Conversion scalor to convert the measure signal into absolute photon numbers.
        This should pre-computed or measured directly on the instrument.
    """

    codec_id: ClassVar[Literal["anscombe-v1"]] = "anscombe-v1"
    zero_level: int
    photon_sensitivity: float
    # TODO: decide if these are class variables or not
    encoded_dtype: str = "uint8"
    decoded_dtype: str = "int16"

    def encode(self, buf: np.ndarray) -> np.ndarray:
        return encode(
            buf,
            sensitivity=self.photon_sensitivity,
            zero_level=self.zero_level,
            encoded_dtype=self.encoded_dtype,
        )

    def decode(self, buf: bytes, out: object | None = None) -> np.ndarray:
        return decode(
            buf,
            sensitivity=self.photon_sensitivity,
            zero_level=self.zero_level,
            encoded_dtype=self.encoded_dtype,
            decoded_dtype=self.decoded_dtype,
        )

    def get_config(self) -> AnscomeCodecJSON_V2:
        return {
            "id": self.codec_id,
            "zero_level": self.zero_level,
            "photon_sensitivity": self.photon_sensitivity,
        }

    @classmethod
    def from_config(cls, config: AnscomeCodecJSON_V2) -> Self:
        return cls(
            zero_level=config["zero_level"],
            photon_sensitivity=config["photon_sensitivity"],
        )


numcodecs.register_codec(AnscombeCodecV2)


@dataclass(frozen=True, slots=True)
class AnscombeCodecV3(ArrayArrayCodec):
    """Zarr v3 codec for Anscombe Transform for photon-limited data.

    Parameters
    ----------
    zero_level : int
        Signal level when no photons are recorded.
    photon_sensitivity : float
        Estimated signal intensity increase per quantum (e.g. photon)
    encoded_dtype : str
        Data type for encoded (compressed) data.
    decoded_dtype : str
        Data type for decoded (original) data.
    """

    zero_level: int
    photon_sensitivity: float
    encoded_dtype: str = "uint8"
    decoded_dtype: str = "int16"
    is_fixed_size: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Create codec instance from configuration dictionary."""
        config = data.get("configuration", {})
        return cls(
            zero_level=config["zero_level"],
            photon_sensitivity=config["photon_sensitivity"],
            encoded_dtype=config.get("encoded_dtype", "uint8"),
            decoded_dtype=config.get("decoded_dtype", "int16"),
        )

    def to_dict(self) -> dict:
        """Convert codec to configuration dictionary."""
        return {
            "name": "anscombe-v1",
            "configuration": {
                "zero_level": self.zero_level,
                "photon_sensitivity": self.photon_sensitivity,
                "encoded_dtype": self.encoded_dtype,
                "decoded_dtype": self.decoded_dtype,
            },
        }

    def resolve_metadata(self, chunk_spec: ArraySpec) -> ArraySpec:
        """Resolve metadata for encoded output."""
        return ArraySpec(
            shape=chunk_spec.shape,
            dtype=parse_dtype(np.dtype(self.encoded_dtype), zarr_format=3),
            fill_value=chunk_spec.fill_value,
            config=chunk_spec.config,
            prototype=chunk_spec.prototype,
        )

    def _encode(self, buf: np.ndarray) -> np.ndarray:
        """Synchronous encode method for direct use."""
        return encode(
            buf,
            sensitivity=self.photon_sensitivity,
            zero_level=self.zero_level,
            encoded_dtype=self.encoded_dtype,
        )

    def _decode(self, buf: np.ndarray) -> np.ndarray:
        """Synchronous decode method for direct use."""
        return decode(
            buf.tobytes(),
            sensitivity=self.photon_sensitivity,
            zero_level=self.zero_level,
            encoded_dtype=self.encoded_dtype,
            decoded_dtype=self.decoded_dtype,
        )

    async def _encode_single(
        self,
        chunk_array,
        chunk_spec,
    ):
        """Encode a single chunk using Anscombe transform."""
        # Convert NDBuffer to numpy array
        data = chunk_array.as_numpy_array()

        # Apply encoding
        encoded = self._encode(data)

        # Return as NDBuffer
        return chunk_array.from_numpy_array(encoded)

    async def _decode_single(
        self,
        chunk_array,
        chunk_spec,
    ):
        """Decode a single chunk using inverse Anscombe transform."""
        # Convert NDBuffer to numpy array
        data = chunk_array.as_numpy_array()

        # Apply decoding
        decoded = self._decode(data)

        # Reshape to original shape
        decoded = decoded.reshape(chunk_spec.shape)

        # Return as NDBuffer
        return chunk_array.from_numpy_array(decoded)


# Register codec with zarr
from zarr.registry import register_codec

register_codec("anscombe-v1", AnscombeCodecV3)
