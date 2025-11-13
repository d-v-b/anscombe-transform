import numpy as np

def make_demo_data(
        *,
        n_frames: int = 50,
        height: int = 256,
        width: int = 256,
        mean_photon_rate: float = 5.0,
        zero_level: float = 20.0,
        conversion_gain: float = 30.0
        ) -> np.ndarray:
    """
    A convenience function for generating synthetic imaging data
    """

    photon_rate = np.random.exponential(scale=mean_photon_rate, size=(1, height, width))
    photon_counts = np.random.poisson(np.tile(photon_rate, (n_frames, 1, 1)))
    measured_signal = photon_counts + np.random.randn(n_frames, height, width) * 0.2

    return (zero_level + conversion_gain * measured_signal).astype('int16')