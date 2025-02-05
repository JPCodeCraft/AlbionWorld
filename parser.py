# extract file using https://github.com/AssetRipper/AssetRipper


import re
import xml.etree.ElementTree as ET
import json
import sys

xml_path = 'world.xml'
output_path = 'albionLocations.json'
cluster_types_path = 'clusterTypes.json'

def type_to_pvp_category(type_str):
    if 'DUNGEON_BLACK' in type_str or 'OPENPVP_BLACK' in type_str or 'PASSAGE_BLACK' in type_str:
        return 'black'
    elif 'DUNGEON_RED' in type_str or 'OPENPVP_RED' in type_str or 'PASSAGE_RED' in type_str:
        return 'red'
    elif 'DUNGEON_YELLOW' in type_str or 'OPENPVP_YELLOW' in type_str:
        return 'yellow'
    elif 'DUNGEON_SAFEAREA' in type_str or 'SAFEAREA' in type_str or 'STARTAREA' in type_str or 'PLAYERCITY' in type_str or 'STARTINGCITY' in type_str or 'TUTORIAL' in type_str:
        return 'blue'
    else:
        return 'other'
    
def type_to_map_category(type_str):
    if 'ARENA' in type_str:
        return 'arena'
    if 'CORRUPTED_DUNGEON' in type_str:
        return 'corrupted'
    if 'DUNGEON' in type_str:
        return 'dungeon'
    if 'ISLAND' in type_str:
        return 'island'
    if 'EXPEDITION' in type_str:
        return 'expedition'
    if 'HIDEOUT' in type_str:
        return 'hideout'
    if 'PLAYERCITY' in type_str or 'STARTINGCITY' in type_str or 'TUTORIAL' in type_str:
        return 'city'
    if 'OPENPVP' in type_str or 'SAFEAREA' in type_str or 'STARTAREA' in type_str:
        return 'openworld'
    if 'PASSAGE' in type_str:
        return 'passage'
    if 'TUNNEL' in type_str:
        return 'roads'
    else:
        return 'other'

def parse_clusters(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    clusters = []
    cluster_types = set()
    
    # Find all cluster elements
    for cluster_elem in root.findall('./clusters/cluster'):
        if cluster_elem.get('enabled') == 'true':
            cluster = {
                'imageFile': cluster_elem.get('file').replace('.cluster.xml', '.png'),
                'id': cluster_elem.get('id'),
                'tier': re.search(r'_T(\d)_', cluster_elem.get('file')).group(1) if re.search(r'_T(\d)_', cluster_elem.get('file')) else None,
                'quality': re.search(r'_Q(\d).', cluster_elem.get('file')).group(1) if re.search(r'_Q(\d).', cluster_elem.get('file')) else None,
                'displayName': cluster_elem.get('displayname'),
                'enabled': cluster_elem.get('enabled'),
                'type': cluster_elem.get('type'),
                'pvpCategory': type_to_pvp_category(cluster_elem.get('type')),
                'mapCategory': type_to_map_category(cluster_elem.get('type')),
                'origin': tuple(map(float, cluster_elem.get('origin').split())) if cluster_elem.get('origin') else None,
                'size': tuple(map(float, cluster_elem.get('size').split())) if cluster_elem.get('size') else None,
                'worldmapposition': tuple(map(float, cluster_elem.get('worldmapposition').split())) if cluster_elem.get('worldmapposition') else None,
                'minimapBoundsMin': tuple(map(float, cluster_elem.get('minimapBoundsMin').split())) if cluster_elem.get('minimapBoundsMin') else None,
                'minimapBoundsMax': tuple(map(float, cluster_elem.get('minimapBoundsMax').split())) if cluster_elem.get('minimapBoundsMax') else None,
                'neighbours': set(),  # Use a set to collect unique neighbours
                'exits': [],
                'portalExits': [],
                'portalEntrances': [],
            }
            # Add idInt property using the specified logic and update displayName for smugglers network
            id_val = cluster['id']
            id_Int = None
            if id_val:
                try:
                    if "BLACKBANK-" in id_val:
                        id_val = id_val.replace("BLACKBANK-", "")
                        id_Int = int(id_val)
                        if id_Int:
                            matching_cluster = root.find(f"./clusters/cluster[@id='{id_Int}']")
                            if matching_cluster:
                                cluster['displayName'] = matching_cluster.get('displayname') + ' Smugglers Network'
                    elif "-Auction2" in id_val:
                        id_val = id_val.replace("-Auction2", "")
                        id_Int = int(id_val)
                    else:
                        id_Int = int(id_val)
                except ValueError:
                    id_Int = None
            cluster['idInt'] = id_Int
            
            cluster_types.add(cluster['type'])

            # Process exits
            exits_elem = cluster_elem.find('exits')
            if exits_elem is not None:
                for exit_elem in exits_elem.findall('exit'):
                    target_id = exit_elem.get('targetid').split('@')[0]
                    target_location_id = exit_elem.get('targetid').split('@')[-1]
                    cluster['neighbours'].add(target_location_id)
                    cluster['exits'].append({                        
                        'id': exit_elem.get('id'),
                        'targetId': target_id,
                        'targetLocationId': target_location_id,
                        'position': tuple(map(float, exit_elem.get('pos').split())),
                    })
            
            # Process portal exits
            portal_exits_elem = cluster_elem.find('portalexits')
            if portal_exits_elem is not None:
                for portal_exit_elem in portal_exits_elem.findall('portalexit'):
                    target_id = portal_exit_elem.get('targetid').split('@')[0]
                    target_location_id = portal_exit_elem.get('targetid').split('@')[-1]
                    cluster['neighbours'].add(target_location_id)
                    cluster['portalExits'].append({                
                        'id': portal_exit_elem.get('id'),
                        'targetId': target_id,
                        'targetLocationId': target_location_id,
                        'position': tuple(map(float, portal_exit_elem.get('pos').split())),
                        'kind': portal_exit_elem.get('kind'),
                    })
                    
            # Process portal entrances
            portal_entrances_elem = cluster_elem.find('portalentrances')
            if portal_entrances_elem is not None:
                for portal_entrance_elem in portal_entrances_elem.findall('portalentrance'):
                    cluster['portalEntrances'].append({                
                        'id': portal_entrance_elem.get('id'),
                        'position': tuple(map(float, portal_entrance_elem.get('pos').split())),
                        'kind': portal_entrance_elem.get('kind'),
                    })
                    
            # Process marketplaces for market property
            marketplaces_elem = cluster_elem.find('marketplaces')
            is_smuggler_network_market = False
            is_market = False
            if marketplaces_elem is not None:
                is_market = True
                for marketplace_elem in marketplaces_elem.findall('marketplace'):
                    if 'BLACKBANK' in marketplace_elem.get('type', ''):
                        is_smuggler_network_market = True
                        break
            cluster['isSmugglersNetworkMarket'] = is_smuggler_network_market
            cluster["isMarket"] = is_market
            
            cluster['neighbours'] = list(cluster['neighbours'])  # Convert set back to list
            clusters.append(cluster)
    
    return clusters, list(cluster_types)

if __name__ == '__main__':
    xml_file = sys.argv[1] if len(sys.argv) > 1 else xml_path
    clusters_data, cluster_types = parse_clusters(xml_file)
    
    # Create a map from cluster ID to cluster data for quick lookup
    cluster_map = {cluster['id']: cluster for cluster in clusters_data}
    
    # Process portal exits to update corresponding portal entrances and neighbours
    for source_cluster in clusters_data:
        for portal_exit in source_cluster['portalExits']:
            target_cluster_id = portal_exit['targetLocationId']
            entrance_id = portal_exit['targetId']
            target_cluster = cluster_map.get(target_cluster_id)
            if not target_cluster:
                continue  # Skip if target cluster not found
            # Find the corresponding portal entrance in target cluster
            for entrance in target_cluster['portalEntrances']:
                if entrance['id'] == entrance_id:
                    # Add targetId and targetLocationId to the entrance
                    entrance['targetId'] = portal_exit['id']
                    entrance['targetLocationId'] = source_cluster['id']
                    # Add source cluster to target's neighbours if not present
                    if source_cluster['id'] not in target_cluster['neighbours']:
                        target_cluster['neighbours'].append(source_cluster['id'])
                    break  # Exit loop once found
    
    # Sort cluster_types by name
    cluster_types.sort()
    
    with open(output_path, 'w') as f:
        json.dump(clusters_data, f, indent=2)
    
    with open(cluster_types_path, 'w') as f:
        json.dump(cluster_types, f, indent=2)
    
    print(f"Data has been saved to {output_path}")
    print(f"Cluster types have been saved to {cluster_types_path}")