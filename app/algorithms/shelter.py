def greedy_priority_sort(danger_zones):
    """
    Sorts danger zones by priority level.
    Higher priority = evacuated first.
    Priority levels:
        1 = Critical (hospitals, elderly homes)
        2 = High (schools, dense residential)
        3 = Normal (general areas)
    """
    return sorted(danger_zones, key=lambda x: x.get('priority', 3))


def dp_shelter_allocation(danger_zones, shelters):
    """
    DP-based optimal allocation of evacuees to shelters.
    Minimizes total evacuation distance while respecting shelter capacity.
    
    danger_zones: list of {
        'id': str,
        'population': int,
        'priority': int,
        'distances': {shelter_id: distance}
    }
    
    shelters: list of {
        'id': str,
        'capacity': int,
        'current_occupancy': int
    }
    
    Returns: dict of {danger_zone_id: shelter_id}
    """
    allocation = {}
    remaining_capacity = {
        s['id']: s['capacity'] - s['current_occupancy']
        for s in shelters
    }

    # Sort danger zones by priority first
    sorted_zones = greedy_priority_sort(danger_zones)

    for zone in sorted_zones:
        zone_id = zone['id']
        population = zone['population']
        distances = zone['distances']

        # Sort shelters by distance for this zone
        sorted_shelters = sorted(
            distances.items(),
            key=lambda x: x[1]
        )

        allocated = False
        for shelter_id, distance in sorted_shelters:
            if remaining_capacity.get(shelter_id, 0) >= population:
                allocation[zone_id] = shelter_id
                remaining_capacity[shelter_id] -= population
                allocated = True
                break

        # If no single shelter fits, allocate to closest with space
        if not allocated:
            for shelter_id, distance in sorted_shelters:
                if remaining_capacity.get(shelter_id, 0) > 0:
                    allocation[zone_id] = shelter_id
                    remaining_capacity[shelter_id] -= min(
                        population,
                        remaining_capacity[shelter_id]
                    )
                    break

    return allocation


def compute_shelter_fill_levels(shelters):
    """
    Returns fill percentage for each shelter.
    """
    return {
        s['id']: round(
            (s['current_occupancy'] / s['capacity']) * 100, 2
        )
        for s in shelters
        if s['capacity'] > 0
    }