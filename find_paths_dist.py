import json
import sys
import math
from heapq import heappop, heappush

VALID_TYPES = {
    "OPENPVP_BLACK", "OPENPVP_RED", "OPENPVP_YELLOW",
    "PASSAGE_BLACK", "PASSAGE_RED", "PLAYERCITY",
    "SAFEAREA", "STARTAREA", "STARTINGCITY"
}

def load_clusters(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def find_shortest_path(clusters, start, end, avoid_type):
    # Filter clusters based on VALID_TYPES and avoid_type
    filtered_clusters = []
    for cluster in clusters:
        cluster_type = cluster['type']
        if isinstance(cluster_type, list):
            type_str = " ".join(cluster_type)
        else:
            type_str = cluster_type
        
        has_valid_type = any(valid_type in type_str for valid_type in VALID_TYPES)
        avoid_type_check = avoid_type not in type_str if avoid_type else True
        
        if has_valid_type and avoid_type_check:
            filtered_clusters.append(cluster)
    
    # Check if start or end clusters are valid
    start_cluster = next((c for c in filtered_clusters if c['id'] == start), None)
    end_cluster = next((c for c in filtered_clusters if c['id'] == end), None)
    if not start_cluster or not end_cluster:
        return None
    
    if start == end:
        return ([{"cluster_id": start, "entry": (start_cluster['origin'][0] + start_cluster['size'][0]/2, start_cluster['origin'][1] + start_cluster['size'][1]/2), "exit": None}], [])

    # Priority queue: (total_cost, current_cluster_id, entry_position, path, exit_positions)
    start_origin = start_cluster['origin']
    start_size = start_cluster['size']
    start_entry = (
        start_origin[0] + start_size[0]/2,
        start_origin[1] + start_size[1]/2
    )
    queue = [(0.0, start, start_entry, [(start, start_entry)], [])]
    seen = {}

    while queue:
        current_cost, current_cluster_id, entry_pos, path, exit_positions = heappop(queue)

        if current_cluster_id == end:
            cluster_info = []
            for i in range(len(path)):
                c_id, c_entry = path[i]
                c_exit = exit_positions[i] if i < len(exit_positions) else None
                cluster_info.append({
                    "cluster_id": c_id,
                    "entry": c_entry,
                    "exit": c_exit
                })
            step_costs = []
            for i in range(len(exit_positions)):
                entry = path[i][1]
                exit = exit_positions[i]
                distance = math.hypot(exit[0] - entry[0], exit[1] - entry[1])
                step_costs.append(distance)
            return (cluster_info, step_costs)

        current_state = (current_cluster_id, entry_pos)
        if current_state in seen and seen[current_state] <= current_cost:
            continue
        seen[current_state] = current_cost

        current_cluster = next((c for c in filtered_clusters if c['id'] == current_cluster_id), None)
        if not current_cluster:
            continue

        # Process all exits and portalExits and portalEntrances
        for exit in current_cluster['exits'] + current_cluster.get('portalExits', []) + current_cluster.get('portalEntrances', []):
            exit_pos = tuple(exit['position'])
            
            # Determine target information
            target_info = None
            uuid_part = None
            target_cluster_id = None
            
            # Check if targetId contains '@' (case 1)
            if 'targetId' in exit and isinstance(exit['targetId'], str) and '@' in exit['targetId']:
                target_info = exit['targetId']
                uuid_part, target_cluster_id = target_info.split('@', 1)
            # Check if targetId and targetLocationId are present (case 2)
            elif 'targetId' in exit and 'targetLocationId' in exit:
                uuid_part = exit['targetId']
                target_cluster_id = exit['targetLocationId']
            else:
                # Skip if neither case applies
                continue
            
            # Find the target cluster
            target_cluster = next((c for c in filtered_clusters if c['id'] == target_cluster_id), None)
            if not target_cluster:
                continue  # Target cluster is invalid or filtered out
            
            # Search for reciprocal exit in target cluster's exits and portalExits
            reciprocal_exit = None
            for e in target_cluster['exits'] + target_cluster.get('portalExits', []):
                if e['id'] == uuid_part:
                    reciprocal_exit = e
                    break
            if not reciprocal_exit:
                continue  # No matching exit found in target cluster
            
            reciprocal_exit_pos = tuple(reciprocal_exit['position'])
            
            # Calculate intra-cluster distance from entry to exit
            intra_distance = math.hypot(
                exit_pos[0] - entry_pos[0],
                exit_pos[1] - entry_pos[1]
            )
            new_cost = current_cost + intra_distance
            new_cluster_id = target_cluster['id']
            new_entry_pos = reciprocal_exit_pos
            new_state = (new_cluster_id, new_entry_pos)
            
            if new_state in seen and seen[new_state] <= new_cost:
                continue
            
            new_path = path + [(new_cluster_id, new_entry_pos)]
            new_exit_positions = exit_positions + [exit_pos]
            heappush(queue, (new_cost, new_cluster_id, new_entry_pos, new_path, new_exit_positions))

    return None

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python find_paths.py <albionLocations.json> <start> <end> [avoid_type]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]
    avoid_type = sys.argv[4] if len(sys.argv) > 4 else ""
    
    clusters = load_clusters(file_path)
    result = find_shortest_path(clusters, start, end, avoid_type)
    
    if result:
        cluster_info, step_costs = result
        id_to_name = {cluster['id']: cluster['displayName'] for cluster in clusters}
        id_to_type = {cluster['id']: cluster['type'] for cluster in clusters}
        
        display_path = []
        for i, ci in enumerate(cluster_info):
            cluster_id = ci['cluster_id']
            name = id_to_name.get(cluster_id, 'Unknown')
            type_ = id_to_type.get(cluster_id, 'Unknown')
            entry = ci['entry']
            exit = ci['exit']
            entry_str = f"({entry[0]:.1f}, {entry[1]:.1f})"
            exit_str = f"({exit[0]:.1f}, {exit[1]:.1f})" if exit else "None"
            cost_str = ""
            if exit is not None:
                cost = step_costs[i]
                cost_str = f" [Cost: {cost:.2f}m]"
            display_line = f"{name} ({cluster_id}, {type_}) - Entry: {entry_str}, Exit: {exit_str}{cost_str}"
            display_path.append(display_line)
        
        print(f"Found path from {start} to {end}:")
        print("\n".join(display_path))
        print(f"Total cost: {sum(step_costs):.2f} meters")
    else:
        print(f"No path found from {start} to {end}")