import osmnx as ox
import networkx as nx

def load_city_graph(city_name="Bhubaneswar, Odisha, India"):
    """
    Loads real road network from OpenStreetMap for a given city.
    Returns:
        G: NetworkX graph
        adj: adjacency dict {node: {neighbor: weight}}
        node_coords: dict {node: (lat, lon)}
        edge_capacities: dict {(u, v): capacity}
    """
    print(f"Loading road network for {city_name}...")
    
    # Download road network
    G = ox.graph_from_place(city_name, network_type='drive')
    
    # Project to UTM for accurate distance calculation
    G = ox.project_graph(G)
    G = ox.project_graph(G, to_crs='epsg:4326')

    # Build adjacency dict with travel time as weight
    adj = {}
    edge_capacities = {}

    for u, v, data in G.edges(data=True):
        length = data.get('length', 1)
        speed = data.get('maxspeed', 30)

        # Handle speed as list or string
        if isinstance(speed, list):
            speed = speed[0]
        try:
            speed = float(str(speed).split()[0])
        except:
            speed = 30.0

        # Travel time in seconds
        travel_time = (length / 1000) / speed * 3600

        if u not in adj:
            adj[u] = {}
        adj[u][v] = travel_time

        # Road capacity based on road type
        highway = data.get('highway', 'residential')
        if isinstance(highway, list):
            highway = highway[0]

        if 'motorway' in str(highway):
            capacity = 2000
        elif 'primary' in str(highway):
            capacity = 1500
        elif 'secondary' in str(highway):
            capacity = 1000
        elif 'tertiary' in str(highway):
            capacity = 500
        else:
            capacity = 200

        edge_capacities[(u, v)] = capacity

    # Node coordinates
    node_coords = {}
    for node, data in G.nodes(data=True):
        node_coords[node] = (data['y'], data['x'])  # (lat, lon)

    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
    return G, adj, node_coords, edge_capacities


def get_nearest_node(node_coords, lat, lon):
    """
    Returns the nearest graph node to given coordinates.
    """
    min_dist = float('inf')
    nearest = None

    for node, (nlat, nlon) in node_coords.items():
        dist = ((nlat - lat)**2 + (nlon - lon)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            nearest = node

    return nearest


def block_road(adj, edge_capacities, node_from, node_to):
    """
    Blocks a road by removing it from adjacency dict.
    Returns updated adj and edge_capacities.
    """
    if node_from in adj and node_to in adj[node_from]:
        del adj[node_from][node_to]
    if (node_from, node_to) in edge_capacities:
        del edge_capacities[(node_from, node_to)]
    
    print(f"Road blocked: {node_from} -> {node_to}")
    return adj, edge_capacities