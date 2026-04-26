import heapq
import math

def heuristic(node_coords, target_coords):
    """
    Haversine distance as heuristic for A*.
    Returns distance in meters between two (lat, lon) points.
    """
    lat1, lon1 = node_coords
    lat2, lon2 = target_coords

    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def astar(graph, start, end, node_coords, blocked_edges=None):
    """
    A* algorithm for shortest path with geographic heuristic.
    graph: dict of {node: {neighbor: weight}}
    node_coords: dict of {node: (lat, lon)}
    blocked_edges: set of (node_from, node_to) tuples to ignore
    Returns: (distance, path)
    """
    if blocked_edges is None:
        blocked_edges = set()

    target_coords = node_coords.get(end, (0, 0))

    # Priority queue: (f_score, node)
    pq = [(0, start)]
    g_score = {start: 0}
    f_score = {start: heuristic(node_coords.get(start, (0, 0)), target_coords)}
    previous = {start: None}
    visited = set()

    while pq:
        _, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            if (current_node, neighbor) in blocked_edges:
                continue

            tentative_g = g_score[current_node] + weight

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                h = heuristic(node_coords.get(neighbor, (0, 0)), target_coords)
                f_score[neighbor] = tentative_g + h
                previous[neighbor] = current_node
                heapq.heappush(pq, (f_score[neighbor], neighbor))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()

    if not path or path[0] != start:
        return float('inf'), []

    return g_score.get(end, float('inf')), path