"""
Anscombe Transform codec for Zarr.

This package provides Zarr v2 and v3 codec implementations for compressing
photon-limited movies using the Anscombe variance-stabilizing transformation.
"""

from . import estimate
from .codec import AnscombeTransformV2, AnscombeTransformV3, decode, encode

__all__ = ["AnscombeTransformV2", "AnscombeTransformV3", "decode", "encode", "estimate"]
