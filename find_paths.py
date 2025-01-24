import json
import sys
from heapq import heappop, heappush

VALID_TYPES = {
    "OPENPVP_BLACK", "OPENPVP_RED", "OPENPVP_YELLOW",
    "PASSAGE_BLACK", "PASSAGE_RED", "PLAYERCITY",
    "SAFEAREA", "STARTAREA", "STARTINGCITY"
}

TYPE_WEIGHTS = {
    "OPENPVP_BLACK": 3,
    "OPENPVP_RED": 3,
    "OPENPVP_YELLOW": 1,
    "PASSAGE_BLACK": 2,
    "PASSAGE_RED": 2,
    "PLAYERCITY": 1,
    "SAFEAREA": 1,
    "STARTAREA": 1,
    "STARTINGCITY": 1
}

def load_clusters(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def find_shortest_path(clusters, start, end, avoid_type):
    # Filter to clusters whose type contains any valid type string
    filtered_clusters = []
    
    for cluster in clusters:
        # Check if the cluster type contains any valid type string
        has_valid_type = any(
            valid_type in cluster['type']
            for valid_type in VALID_TYPES
        )
        # Check if the cluster type does not contain the avoid_type (if specified)
        avoid_type_check = avoid_type not in " ".join(cluster['type']) if avoid_type else True
        
        if has_valid_type and avoid_type_check:
            filtered_clusters.append(cluster)                

    # Build graph and cost for valid clusters
    graph = {}
    cluster_cost = {}
    for c in filtered_clusters:
        graph[c['id']] = c['neighbours']
        cluster_cost[c['id']] = min(
            TYPE_WEIGHTS[vt]
            for vt in TYPE_WEIGHTS
            if vt in c['type']
        ) if any(vt in c['type'] for vt in TYPE_WEIGHTS) else 1

    queue = [(0, start, [])]
    seen = {}

    while queue:
        cost, node, path = heappop(queue)
        if node in seen and seen[node] <= cost:
            continue
        path = path + [node]
        seen[node] = cost
        if node == end:
            return path
        for neighbour in graph.get(node, []):
            next_cost = cost + cluster_cost.get(neighbour, 1)
            if neighbour not in seen or next_cost < seen[neighbour]:
                heappush(queue, (next_cost, neighbour, path))

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
    path = find_shortest_path(clusters, start, end, avoid_type)

    if path:
        id_to_name = {cluster['id']: cluster['displayName'] for cluster in clusters}
        id_to_type = {cluster['id']: cluster['type'] for cluster in clusters}
        display_path = [f"{id_to_name[node]} ({node}, {id_to_type[node]})" for node in path]
        print(f"Found path from {start} to {end}:")
        print(" -> ".join(display_path))
    else:
        print(f"No path found from {start} to {end}")