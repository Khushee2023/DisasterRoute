from pydantic import BaseModel
from typing import List, Optional

class ShelterModel(BaseModel):
    name: str
    lat: float
    lon: float
    capacity: int
    current_occupancy: int = 0

class DangerZoneModel(BaseModel):
    id: str
    lat: float
    lon: float
    population: int
    priority: int = 3  # 1=Critical, 2=High, 3=Normal

class ScenarioModel(BaseModel):
    name: str
    city: str = "Bhubaneswar, Odisha, India"
    shelters: List[ShelterModel]
    danger_zones: List[DangerZoneModel]

class BlockRoadModel(BaseModel):
    scenario_id: int
    node_from: int
    node_to: int

class EvacuationRequestModel(BaseModel):
    scenario_id: int
    algorithm: str = "astar"  # "dijkstra" or "astar"

class RouteResponseModel(BaseModel):
    danger_zone_id: str
    shelter_name: str
    algorithm: str
    distance: float
    path_coords: List[List[float]]
    priority: int

class ScenarioResponseModel(BaseModel):
    scenario_id: int
    routes: List[RouteResponseModel]
    shelter_fill_levels: dict
    max_flow_results: dict
    total_evacuation_time: float