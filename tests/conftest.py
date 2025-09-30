from __future__ import annotations
import numpy as np

def nearly_equal(a: np.ndarray, b:np.ndarray, sensitivity: int) -> bool:
        """
        Compare if two arrays are approximately equal within a tolerance.
        The arrays are linearized before comparison.
        """
        return np.allclose(a.ravel(), b.ravel(), atol=sensitivity/2, rtol=0)