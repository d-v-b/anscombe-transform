from __future__ import annotations
import numpy as np

def nearly_equal(a: np.ndarray, b:np.ndarray, sensitivity: float) -> bool:
        """
        Compare if two arrays are approximately equal within a tolerance.
        The arrays are linearized before comparison.
        """
        return np.allclose(np.array(a).ravel(), b.ravel(), atol=sensitivity, rtol=0)