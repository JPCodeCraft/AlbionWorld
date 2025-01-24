import json
import sys
from heapq import heappop, heappush

def load_clusters(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def find_shortest_path(clusters, start, end, avoid_type):
    if avoid_type:
        graph = {cluster['id']: cluster['neighbours'] for cluster in clusters if avoid_type not in cluster['type']}
    else:
        graph = {cluster['id']: cluster['neighbours'] for cluster in clusters}
    
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
            if neighbour not in seen or cost + 1 < seen[neighbour]:
                heappush(queue, (cost + 1, neighbour, path))

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
        display_path = [f"{id_to_name[node]} ({node})" for node in path]
        print(f"Found path from {start} to {end}:")
        print(" -> ".join(display_path))
    else:
        print(f"No path found from {start} to {end}")