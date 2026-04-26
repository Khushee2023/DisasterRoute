import heapq

def dijkstra(graph, start, end, blocked_edges=None):
    """
    Dijkstra's algorithm for shortest path.
    graph: dict of {node: {neighbor: weight}}
    blocked_edges: set of (node_from, node_to) tuples to ignore
    Returns: (distance, path)
    """
    if blocked_edges is None:
        blocked_edges = set()

    # Priority queue: (distance, node)
    pq = [(0, start)]
    distances = {start: 0}
    previous = {start: None}
    visited = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            # Skip blocked roads
            if (current_node, neighbor) in blocked_edges:
                continue

            distance = current_dist + weight

            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()

    if path[0] != start:
        return float('inf'), []

    return distances.get(end, float('inf')), path