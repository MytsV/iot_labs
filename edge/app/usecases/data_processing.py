from collections import deque
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

z_history = deque(maxlen=5)
THRESHOLD = 2000

def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """

    z_value = agent_data.accelerometer.z
    prev_z = z_history[-1] if z_history else z_value

    z_history.append(z_value)

    z_diff = prev_z - z_value
    is_pothole = z_diff > THRESHOLD

    road_state = "rough" if is_pothole else "smooth"

    processed_data = ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )

    return processed_data
