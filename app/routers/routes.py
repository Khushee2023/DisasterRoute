from fastapi import APIRouter, HTTPException
from app.models import (
    ScenarioModel, EvacuationRequestModel,
    BlockRoadModel, RouteResponseModel, ScenarioResponseModel
)
from app.database import get_connection
from app.algorithms.dijkstra import dijkstra
from app.algorithms.astar import astar
from app.algorithms.maxflow import compute_evacuation_capacities
from app.algorithms.shelter import (
    dp_shelter_allocation, compute_shelter_fill_levels
)
from app.data.graph_loader import load_city_graph, get_nearest_node, block_road

router = APIRouter()

# In-memory graph cache
graph_cache = {}


@router.post("/scenario/create")
def create_scenario(scenario: ScenarioModel):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO scenarios (name, city) VALUES (?, ?)",
        (scenario.name, scenario.city)
    )
    scenario_id = cursor.lastrowid

    for shelter in scenario.shelters:
        cursor.execute(
            """INSERT INTO shelters 
            (scenario_id, name, lat, lon, capacity, current_occupancy)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (scenario_id, shelter.name, shelter.lat, shelter.lon,
             shelter.capacity, shelter.current_occupancy)
        )

    conn.commit()
    conn.close()

    # Load graph for this city and cache it
    G, adj, node_coords, edge_capacities = load_city_graph(scenario.city)
    graph_cache[scenario_id] = {
        'G': G,
        'adj': adj,
        'node_coords': node_coords,
        'edge_capacities': edge_capacities,
        'blocked_edges': set(),
        'shelters': scenario.shelters,
        'danger_zones': scenario.danger_zones
    }

    return {"scenario_id": scenario_id, "message": "Scenario created successfully"}


@router.post("/evacuate")
def evacuate(request: EvacuationRequestModel):
    scenario_id = request.scenario_id
    algorithm = request.algorithm

    if scenario_id not in graph_cache:
        raise HTTPException(status_code=404, detail="Scenario not found")

    cache = graph_cache[scenario_id]
    adj = cache['adj']
    node_coords = cache['node_coords']
    edge_capacities = cache['edge_capacities']
    blocked_edges = cache['blocked_edges']
    shelters = cache['shelters']
    danger_zones = cache['danger_zones']

    conn = get_connection()
    cursor = conn.cursor()

    # Get shelter nodes
    shelter_nodes = []
    for shelter in shelters:
        node = get_nearest_node(node_coords, shelter.lat, shelter.lon)
        shelter_nodes.append({
            'id': shelter.name,
            'node': node,
            'capacity': shelter.capacity,
            'current_occupancy': shelter.current_occupancy,
            'lat': shelter.lat,
            'lon': shelter.lon
        })

    # Get danger zone nodes and distances to shelters
    dz_data = []
    for dz in danger_zones:
        dz_node = get_nearest_node(node_coords, dz.lat, dz.lon)
        distances = {}

        for s in shelter_nodes:
            if algorithm == "dijkstra":
                dist, _ = dijkstra(adj, dz_node, s['node'], blocked_edges)
            else:
                dist, _ = astar(adj, dz_node, s['node'], node_coords, blocked_edges)
            distances[s['id']] = dist

        dz_data.append({
            'id': dz.id,
            'node': dz_node,
            'population': dz.population,
            'priority': dz.priority,
            'distances': distances
        })

    # DP shelter allocation
    allocation = dp_shelter_allocation(dz_data, [
        {'id': s['id'], 'capacity': s['capacity'],
         'current_occupancy': s['current_occupancy']}
        for s in shelter_nodes
    ])

    # Compute routes
    routes = []
    max_time = 0

    for dz in dz_data:
        shelter_id = allocation.get(dz['id'])
        if not shelter_id:
            continue

        shelter_node = next(s['node'] for s in shelter_nodes if s['id'] == shelter_id)

        if algorithm == "dijkstra":
            dist, path = dijkstra(adj, dz['node'], shelter_node, blocked_edges)
        else:
            dist, path = astar(adj, dz['node'], shelter_node, node_coords, blocked_edges)

        # Convert path nodes to coordinates
        path_coords = [
            [node_coords[n][0], node_coords[n][1]]
            for n in path if n in node_coords
        ]

        if dist > max_time:
            max_time = dist

        # Store in DB
        cursor.execute(
            """INSERT INTO evacuations
            (scenario_id, origin_lat, origin_lon, shelter_id, algorithm, distance)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (scenario_id, dz_data[0]['node'], dz_data[0]['node'],
             0, algorithm, dist)
        )

        routes.append(RouteResponseModel(
            danger_zone_id=dz['id'],
            shelter_name=shelter_id,
            algorithm=algorithm,
            distance=round(dist, 2),
            path_coords=path_coords,
            priority=dz['priority']
        ))

    # Max flow
    danger_nodes = [dz['node'] for dz in dz_data]
    shelter_node_ids = [s['node'] for s in shelter_nodes]
    max_flow_results = compute_evacuation_capacities(
        adj, edge_capacities, danger_nodes, shelter_node_ids
    )
    max_flow_serializable = {
        f"{k[0]}-{k[1]}": v for k, v in max_flow_results.items()
    }

    # Shelter fill levels
    updated_shelters = []
    for s in shelter_nodes:
        allocated_pop = sum(
            dz['population'] for dz in dz_data
            if allocation.get(dz['id']) == s['id']
        )
        updated_shelters.append({
            'id': s['id'],
            'capacity': s['capacity'],
            'current_occupancy': s['current_occupancy'] + allocated_pop
        })

    fill_levels = compute_shelter_fill_levels(updated_shelters)

    conn.commit()
    conn.close()

    return ScenarioResponseModel(
        scenario_id=scenario_id,
        routes=routes,
        shelter_fill_levels=fill_levels,
        max_flow_results=max_flow_serializable,
        total_evacuation_time=round(max_time, 2)
    )


@router.post("/block-road")
def block_road_endpoint(request: BlockRoadModel):
    scenario_id = request.scenario_id

    if scenario_id not in graph_cache:
        raise HTTPException(status_code=404, detail="Scenario not found")

    cache = graph_cache[scenario_id]
    cache['blocked_edges'].add((request.node_from, request.node_to))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO blocked_roads (scenario_id, node_from, node_to) VALUES (?, ?, ?)",
        (scenario_id, request.node_from, request.node_to)
    )
    conn.commit()
    conn.close()

    return {"message": f"Road blocked: {request.node_from} -> {request.node_to}"}


@router.get("/scenario/{scenario_id}/shelters")
def get_shelters(scenario_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM shelters WHERE scenario_id = ?", (scenario_id,)
    )
    shelters = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"shelters": shelters}


@router.get("/scenario/{scenario_id}/blocked-roads")
def get_blocked_roads(scenario_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM blocked_roads WHERE scenario_id = ?", (scenario_id,)
    )
    roads = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"blocked_roads": roads}