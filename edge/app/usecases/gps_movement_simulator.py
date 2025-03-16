import math
from datetime import datetime
import random
from typing import Tuple, Dict


class GpsMovementSimulator:
    """
    Simulates realistic GPS movement for users at normal car speeds.
    """
    def __init__(self):
        # Store user starting positions and current positions
        self.user_positions: Dict[str, Tuple[float, float]] = {}
        # Store previous timestamp for each user
        self.prev_timestamps: Dict[str, datetime] = {}
        # Store user headings (in degrees, 0 = North, 90 = East)
        self.user_headings: Dict[str, float] = {}
        # Average car speed in meters per second (30-60 km/h in urban areas)
        self.avg_speed_mps = random.uniform(8, 17)  # ~30-60 km/h
        # Slight variations in speed
        self.speed_variation = 0.2  # 20% variation
        # Probability to change direction at any step
        self.turn_probability = 0.015

    def _initialize_user(self, user_id: str) -> None:
        """Initialize a new user with random starting position."""
        # Random starting positions - using a reasonable GPS area
        # These values create positions around San Francisco as an example
        lat = random.uniform(37.75, 37.80)  # latitude range
        lng = random.uniform(-122.45, -122.40)  # longitude range
        self.user_positions[user_id] = (lat, lng)
        # Random initial heading
        self.user_headings[user_id] = random.uniform(0, 360)

    def _get_new_position(self, lat: float, lng: float, heading: float,
                          distance_meters: float) -> Tuple[float, float]:
        """
        Calculate new position based on current position, heading and distance.

        Args:
            lat: Current latitude
            lng: Current longitude
            heading: Direction of movement in degrees (0=North, 90=East)
            distance_meters: Distance to move in meters

        Returns:
            Tuple of (new_latitude, new_longitude)
        """
        # Earth's radius in meters
        R = 6378137

        # Convert heading from degrees to radians
        heading_rad = math.radians(heading)

        # Convert latitude and longitude from degrees to radians
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)

        # Calculate new latitude
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(distance_meters / R) +
            math.cos(lat_rad) * math.sin(distance_meters / R) * math.cos(heading_rad)
        )

        # Calculate new longitude
        new_lng_rad = lng_rad + math.atan2(
            math.sin(heading_rad) * math.sin(distance_meters / R) * math.cos(lat_rad),
            math.cos(distance_meters / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )

        # Convert back to degrees
        new_lat = math.degrees(new_lat_rad)
        new_lng = math.degrees(new_lng_rad)

        return new_lat, new_lng

    def update_position(self, user_id: str, timestamp: datetime) -> Tuple[float, float]:
        """
        Update the user's position based on elapsed time since the last update.

        Args:
            user_id: Unique identifier for the user
            timestamp: Current timestamp

        Returns:
            Tuple of (latitude, longitude)
        """
        # Initialize user if they don't exist
        if user_id not in self.user_positions:
            self._initialize_user(user_id)
            self.prev_timestamps[user_id] = timestamp
            return self.user_positions[user_id]

        # Calculate time difference in seconds
        prev_time = self.prev_timestamps.get(user_id, timestamp)
        time_diff_seconds = (timestamp - prev_time).total_seconds()

        # Skip if timestamp is the same or earlier than previous
        if time_diff_seconds <= 0:
            return self.user_positions[user_id]

        # Current position and heading
        current_lat, current_lng = self.user_positions[user_id]
        current_heading = self.user_headings[user_id]

        # Randomly change direction sometimes (simulating turns)
        if random.random() < self.turn_probability:
            # Change heading by -90 to +90 degrees
            turn_angle = random.uniform(-90, 90)
            current_heading = (current_heading + turn_angle) % 360
            self.user_headings[user_id] = current_heading

        # Calculate speed with some variation
        speed = self.avg_speed_mps * (1 + random.uniform(-self.speed_variation, self.speed_variation))

        # Calculate distance traveled
        distance = speed * time_diff_seconds

        # Get new position
        new_lat, new_lng = self._get_new_position(
            current_lat, current_lng, current_heading, distance
        )

        # Update user's position
        self.user_positions[user_id] = (new_lat, new_lng)
        self.prev_timestamps[user_id] = timestamp

        return new_lat, new_lng
