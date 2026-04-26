from collections import defaultdict, deque

def bfs(capacity, source, sink, parent):
    """
    BFS to find augmenting path in residual graph.
    Returns True if path exists from source to sink.
    """
    visited = set([source])
    queue = deque([source])

    while queue:
        node = queue.popleft()

        for neighbor in capacity[node]:
            if neighbor not in visited and capacity[node][neighbor] > 0:
                visited.add(neighbor)
                parent[neighbor] = node
                if neighbor == sink:
                    return True
                queue.append(neighbor)

    return False

def ford_fulkerson(graph, source, sink, edge_capacities):
    """
    Ford-Fulkerson Max Flow algorithm.
    Determines maximum evacuee flow from source to sink.
    
    graph: dict of {node: [neighbors]}
    source: starting node (danger zone)
    sink: ending node (shelter)
    edge_capacities: dict of {(node_from, node_to): capacity}
    
    Returns: max_flow (int)
    """
    # Build capacity residual graph
    capacity = defaultdict(lambda: defaultdict(int))

    for (u, v), cap in edge_capacities.items():
        capacity[u][v] += cap
        capacity[v][u] += 0  # reverse edge starts at 0

    max_flow = 0

    while True:
        parent = {}
        if not bfs(capacity, source, sink, parent):
            break

        # Find minimum capacity along the path
        path_flow = float('inf')
        node = sink
        while node != source:
            prev = parent[node]
            path_flow = min(path_flow, capacity[prev][node])
            node = prev

        # Update capacities along the path
        node = sink
        while node != source:
            prev = parent[node]
            capacity[prev][node] -= path_flow
            capacity[node][prev] += path_flow
            node = prev

        max_flow += path_flow

    return max_flow


def compute_evacuation_capacities(graph, road_capacities, danger_zones, shelters):
    """
    Computes max flow from all danger zones to all shelters.
    Returns dict of {(danger_zone, shelter): max_flow}
    """
    results = {}

    for dz in danger_zones:
        for shelter in shelters:
            flow = ford_fulkerson(graph, dz, shelter, road_capacities)
            results[(dz, shelter)] = flow

    return results