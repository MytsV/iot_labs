from pydantic import BaseModel
from app.entities.agent_data import AgentData


class GpsData(BaseModel):
    latitude: float
    longitude: float


class ExtendedAgentData(AgentData):
    gps: GpsData


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: ExtendedAgentData
