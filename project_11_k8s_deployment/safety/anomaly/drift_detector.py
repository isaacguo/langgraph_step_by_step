import numpy as np
from typing import List, Union
from scipy import stats

class DriftDetector:
    def __init__(self, window_size: int = 100, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold
        self.reference_window: List[float] = []
        self.current_window: List[float] = []

    def add_data_point(self, value: float):
        self.current_window.append(value)
        if len(self.current_window) > self.window_size:
            self.current_window.pop(0)

    def set_reference(self, data: List[float]):
        self.reference_window = data

    def detect_drift(self) -> bool:
        """
        Detect statistical drift using Z-score or KS-test.
        """
        if len(self.reference_window) < 10 or len(self.current_window) < 10:
            return False

        # Method 1: Z-score of means
        ref_mean = np.mean(self.reference_window)
        ref_std = np.std(self.reference_window)
        curr_mean = np.mean(self.current_window)
        
        if ref_std == 0:
            z_score = 0 if curr_mean == ref_mean else float('inf')
        else:
            z_score = abs(curr_mean - ref_mean) / ref_std

        if z_score > self.threshold:
            return True

        # Method 2: KS Test (Distribution comparison)
        statistic, p_value = stats.ks_2samp(self.reference_window, self.current_window)
        if p_value < 0.05: # Significant difference
            return True
            
        return False
