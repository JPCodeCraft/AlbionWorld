import xml.etree.ElementTree as ET
import json
import sys

xml_path = 'world.xml'
output_path = 'albionLocations.json'
cluster_types_path = 'clusterTypes.json'

def parse_clusters(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    clusters = []
    cluster_types = set()
    
    # Find all cluster elements
    for cluster_elem in root.findall('./clusters/cluster'):
        if cluster_elem.get('enabled') == 'true':
            cluster = {
                'id': cluster_elem.get('id'),
                'displayName': cluster_elem.get('displayname'),
                'enabled': cluster_elem.get('enabled'),
                'type': cluster_elem.get('type'),
                'neighbours': set()  # Use a set to collect unique neighbours
            }
            
            cluster_types.add(cluster['type'])
            
            # Process exits
            exits_elem = cluster_elem.find('exits')
            if exits_elem is not None:
                for exit_elem in exits_elem.findall('exit'):
                    target_id = exit_elem.get('targetid').split('@')[-1]
                    cluster['neighbours'].add(target_id)
            
            # Process portal exits
            portal_exits_elem = cluster_elem.find('portalexits')
            if portal_exits_elem is not None:
                for portal_exit_elem in portal_exits_elem.findall('portalexit'):
                    target_id = portal_exit_elem.get('targetid').split('@')[-1]
                    cluster['neighbours'].add(target_id)
            
            cluster['neighbours'] = list(cluster['neighbours'])  # Convert set back to list
            clusters.append(cluster)
    
    return clusters, list(cluster_types)

if __name__ == '__main__':
    xml_file = sys.argv[1] if len(sys.argv) > 1 else xml_path
    clusters_data, cluster_types = parse_clusters(xml_file)
    
    # Sort cluster_types by name
    cluster_types.sort()
    
    with open(output_path, 'w') as f:
        json.dump(clusters_data, f, indent=2)
    
    with open(cluster_types_path, 'w') as f:
        json.dump(cluster_types, f, indent=2)
    
    print(f"Data has been saved to {output_path}")
    print(f"Cluster types have been saved to {cluster_types_path}")