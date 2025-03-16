from collections import deque
from typing import Optional, Tuple
import numpy as np

Z_HISTORY_SIZE = 10  # Increased history size for better context
THRESHOLD_POTHOLE = 1000  # Will be dynamically adjusted if using adaptive thresholds
THRESHOLD_BUMP = 800  # Will be dynamically adjusted if using adaptive thresholds
MIN_EVENT_INTERVAL = 5  # Minimum number of readings between events to reduce duplicates
SMOOTHING_FACTOR = 0.3  # For exponential smoothing

class RoadEventDetector:
    def __init__(self, adaptive_thresholds=True, calibration_period=100):
        self.z_history = deque(maxlen=Z_HISTORY_SIZE)
        self.smoothed_z = None
        self.last_event_idx = -MIN_EVENT_INTERVAL
        self.reading_count = 0
        self.baseline_values = []
        self.baseline_std = None
        self.baseline_mean = None
        self.adaptive_thresholds = adaptive_thresholds
        self.calibration_period = calibration_period
        self.threshold_pothole = THRESHOLD_POTHOLE
        self.threshold_bump = THRESHOLD_BUMP

    def update_adaptive_thresholds(self):
        """Dynamically adjust thresholds based on recent data statistics"""
        if len(self.baseline_values) >= self.calibration_period:
            self.baseline_std = np.std(self.baseline_values)
            self.baseline_mean = np.mean(self.baseline_values)
            # Set thresholds based on statistics of observed data
            self.threshold_pothole = max(THRESHOLD_POTHOLE, 4.5 * self.baseline_std)
            self.threshold_bump = max(THRESHOLD_BUMP, 3.5 * self.baseline_std)
            # Keep only the most recent half of values for future updates
            self.baseline_values = self.baseline_values[-(self.calibration_period//2):]

    def smooth_signal(self, z_value):
        """Apply exponential smoothing to reduce noise"""
        if self.smoothed_z is None:
            self.smoothed_z = z_value
        else:
            self.smoothed_z = SMOOTHING_FACTOR * z_value + (1 - SMOOTHING_FACTOR) * self.smoothed_z
        return self.smoothed_z

    def detect_pattern(self) -> Optional[Tuple[str, float]]:
        """
        Look for characteristic patterns in the z history
        Returns: (event_type, confidence) or None if no pattern detected
        """
        if len(self.z_history) < 5:
            return None

        # Get last 5 readings
        recent = list(self.z_history)[-5:]

        # Pattern for pothole: a significant dip followed by recovery
        # [normal, normal, sharp drop, slight recovery, further recovery]
        if (recent[2] < recent[1] - self.threshold_pothole * 0.8 and
                recent[2] < recent[3] < recent[4]):
            pothole_confidence = min(1.0, abs(recent[1] - recent[2]) / self.threshold_pothole)
            if pothole_confidence > 0.7:
                return ("pothole", pothole_confidence)

        # Pattern for bump: rise then fall
        # [normal, rising, peak, falling, further falling]
        bump_confidence = 0
        if (recent[1] < recent[2] < recent[3] and
                recent[3] > recent[4] and
                abs(recent[3] - recent[1]) > self.threshold_bump * 0.7):
            bump_confidence = min(1.0, abs(recent[3] - recent[1]) / self.threshold_bump)
            if bump_confidence > 0.6:
                return ("bump", bump_confidence)

        return None

    def process_reading(self, z_value):
        """
        Process a single gyroscope z-axis reading
        Returns: road_state, confidence
        """
        # Apply smoothing to reduce noise
        smoothed_z = self.smooth_signal(z_value)

        # Store raw value in history for pattern detection
        self.z_history.append(z_value)
        self.reading_count += 1

        # During calibration period, just collect data
        if self.reading_count < self.calibration_period:
            self.baseline_values.append(z_value)
            return "normal", 0.0

        # For adaptive thresholds, store normal driving values
        if self.adaptive_thresholds:
            # Only use values from normal driving for baseline
            prev_z = self.z_history[-2] if len(self.z_history) > 1 else z_value
            z_diff = abs(z_value - prev_z)
            if z_diff < min(self.threshold_bump, self.threshold_pothole) * 0.3:
                self.baseline_values.append(z_value)
                self.update_adaptive_thresholds()

        # Check if enough time has passed since last event
        if self.reading_count - self.last_event_idx <= MIN_EVENT_INTERVAL:
            return "normal", 0.0

        # Check for patterns first (more reliable than simple thresholds)
        pattern_result = self.detect_pattern()
        if pattern_result:
            self.last_event_idx = self.reading_count
            return pattern_result

        # Fallback to threshold detection if no pattern found
        if len(self.z_history) >= 2:
            prev_z = self.z_history[-2]
            z_diff = z_value - prev_z

            if z_diff < -self.threshold_pothole:
                self.last_event_idx = self.reading_count
                confidence = min(1.0, abs(z_diff) / self.threshold_pothole)
                return "pothole", confidence
            elif z_diff > self.threshold_bump:
                if len(self.z_history) >= 3 and self.z_history[-3] < self.z_history[-2]:
                    self.last_event_idx = self.reading_count
                    confidence = min(1.0, abs(z_diff) / self.threshold_bump)
                    return "bump", confidence

        return "normal", 0.0