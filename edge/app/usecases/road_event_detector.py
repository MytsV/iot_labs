from dataclasses import field, dataclass
from datetime import datetime
from typing import Dict, Optional, List, Tuple


@dataclass
class WindowData:
    start_time: datetime
    end_time: Optional[datetime] = None
    readings: List[Tuple[datetime, float]] = field(default_factory=list)
    max_value: float = 0
    min_value: float = 0
    max_timestamp: Optional[datetime] = None
    min_timestamp: Optional[datetime] = None


class RoadEventDetector:
    """
    Detector for road events (potholes and bumps) based on gyroscope data.
    Processes gyroscope readings in 2-second non-overlapping windows.
    """

    def __init__(self, threshold: float = 50000, window_size_seconds: int = 2):
        """
        Initialize the road event detector.
        
        Parameters:
            threshold: Threshold for detecting significant spikes in gyroscope z-axis
            window_size_seconds: Size of the time window for analysis in seconds
        """
        self.threshold = threshold
        self.window_size = window_size_seconds

        # Store current window data for each user
        self.user_windows: Dict[int, WindowData] = {}

        # Cache detected events for reference
        self.detected_events = []

    def process_reading(self, user_id: int, timestamp: datetime, z_value: float) -> str:
        """
        Process a single gyroscope reading and detect road events.
        
        Parameters:
            user_id: Unique identifier for the user/device
            timestamp: Timestamp of the reading
            z_value: Z-axis gyroscope value
        
        Returns:
            Tuple of (road_state, confidence) where confidence is always 1.0 for detected events
        """
        # Initialize window for this user if not exists
        if user_id not in self.user_windows:
            self.user_windows[user_id] = WindowData(start_time=timestamp)

        current_window = self.user_windows[user_id]

        # Check if this reading belongs to the current window
        time_diff = (timestamp - current_window.start_time).total_seconds()

        # If we've exceeded the window, process the previous window and start a new one
        if time_diff >= self.window_size:
            # Process the completed window
            road_state = self._process_completed_window(user_id)

            # Start a new window
            self.user_windows[user_id] = WindowData(start_time=timestamp)

            # Add this reading to the new window
            self._update_window_with_reading(self.user_windows[user_id], timestamp, z_value)

            return road_state

        # Add the reading to the current window
        self._update_window_with_reading(current_window, timestamp, z_value)

        # By default, return normal state until we have a full window
        return "normal"

    def _update_window_with_reading(self, window: WindowData, timestamp: datetime, z_value: float):
        """Update window data with a new reading"""
        window.readings.append((timestamp, z_value))

        # Update max/min values if needed
        if len(window.readings) == 1 or z_value > window.max_value:
            window.max_value = z_value
            window.max_timestamp = timestamp

        if len(window.readings) == 1 or z_value < window.min_value:
            window.min_value = z_value
            window.min_timestamp = timestamp

        # Update end time
        window.end_time = timestamp

    def _process_completed_window(self, user_id: int) -> str:
        """Process a completed window and determine if there's a road event"""
        window = self.user_windows[user_id]

        # Default state
        road_state = "normal"

        # Check if values exceed threshold
        if abs(window.max_value) > self.threshold or abs(window.min_value) > self.threshold:
            # Calculate magnitude (difference between max and min)
            magnitude = window.max_value - window.min_value

            # Determine event type based on timing of max/min values
            if window.max_timestamp < window.min_timestamp:  # max then min = bump
                road_state = "bump"
            else:  # min then max = pothole
                road_state = "pothole"

            # Store the detected event
            self.detected_events.append({
                'user_id': user_id,
                'event_type': road_state,
                'timestamp': window.max_timestamp if road_state == "bump" else window.min_timestamp,
                'magnitude': magnitude,
                'window_start': window.start_time,
                'window_end': window.end_time
            })

        return road_state
