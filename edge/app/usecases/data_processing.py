from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData, ExtendedAgentData, GpsData
from app.usecases.road_event_detector import RoadEventDetector
from app.usecases.gps_movement_simulator import GpsMovementSimulator


def process_agent_data(
        agent_data: AgentData,
        detector: RoadEventDetector,
        gps_simulator: GpsMovementSimulator
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data containing gyroscope, GPS, and timestamp.
        detector (RoadEventDetector): Persistent detector object for tracking state
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state
        of the road surface and agent data.
    """
    z_value = agent_data.gyroscope.z
    road_state, confidence = detector.process_reading(z_value)

    latitude, longitude = gps_simulator.update_position(
        user_id=agent_data.user_id,
        timestamp=agent_data.timestamp
    )

    gps_data = GpsData(
        latitude=latitude,
        longitude=longitude
    )

    extended_agent_data = ExtendedAgentData(
        **agent_data.dict(),
        gps=gps_data
    )

    processed_data = ProcessedAgentData(
        road_state=road_state,
        confidence=confidence,  # Added confidence score
        agent_data=extended_agent_data
    )

    return processed_data
