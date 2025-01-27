import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import json
import os
from scipy.ndimage import rotate

albionLocationsJsonFile = 'albionLocations.json'
clusterId = '0301'  # Replace with the desired cluster ID

# Load the JSON data
with open(albionLocationsJsonFile, 'r') as f:
    locations = json.load(f)

# Find the cluster with the specified ID
cluster = None
for loc in locations:
    if loc.get('id') == clusterId:
        cluster = loc
        break

if not cluster:
    raise ValueError(f"Cluster with id {clusterId} not found.")

# Extract necessary information from the cluster
image_filename = cluster['imageFile']
exits = cluster.get('exits', [])
portal_exits = cluster.get('portalExits', [])
all_exits = exits + portal_exits
minimap_bounds_min = cluster['minimapBoundsMin']
minimap_bounds_max = cluster['minimapBoundsMax']

x_min, y_min = minimap_bounds_min[0], minimap_bounds_min[1]
x_max, y_max = minimap_bounds_max[0], minimap_bounds_max[1]

# Prepare exits data
exits_data = []
for e in all_exits:
    pos = e['position']
    exits_data.append({
        "id": e['id'],
        "pos": (pos[0], pos[1])
    })

# Construct image path
base_image_dir = r'C:\Users\augus\Downloads\albion assets\ExportedProject\Assets\Resources\generated\maps'
image_path = os.path.join(base_image_dir, image_filename)

# Load the original image
img_original = mpimg.imread(image_path)
original_height, original_width, _ = img_original.shape

# Function to convert game coordinates to original image coordinates using cluster's minimap bounds
def convert_to_image_coords(x_game, y_game, img_width, img_height):
    img_x = (y_game - y_min) / (y_max - y_min) * img_width
    img_y = img_height - (x_game - x_min) / (x_max - x_min) * img_height
    return img_x, img_y

# Convert exits to original image coordinates
original_exits = []
for exit in exits_data:
    x, y = exit["pos"]
    img_x, img_y = convert_to_image_coords(x, y, original_width, original_height)
    original_exits.append((img_x, img_y))

# Rotate the original image
rotated_img = rotate(img_original, angle=45, reshape=True)
rotated_height, rotated_width, _ = rotated_img.shape

# Compute rotated exits
theta = np.radians(45)
cx_original = (original_width - 1) / 2
cy_original = (original_height - 1) / 2
cx_rot = (rotated_width - 1) / 2
cy_rot = (rotated_height - 1) / 2

rotated_exits = []
for (x, y) in original_exits:
    x_centered = x - cx_original
    y_centered = y - cy_original
    x_rot = x_centered * np.cos(theta) - y_centered * np.sin(theta)
    y_rot = x_centered * np.sin(theta) + y_centered * np.cos(theta)
    x_rotated = x_rot + cx_rot
    y_rotated = y_rot + cy_rot
    rotated_exits.append((x_rotated, y_rotated))

# Flip the rotated image vertically
img = np.flipud(rotated_img)
img_height, img_width, _ = img.shape

# Flip the exits vertically to match the flipped image
flipped_exits = [(x, img_height - 1 - y) for (x, y) in rotated_exits]

# Plot the image and exits
fig, ax = plt.subplots()
ax.imshow(img)

for exit, (x, y) in zip(exits_data, flipped_exits):
    ax.plot(x, y, 'ro')  # Plot exit points
    ax.text(x, y, exit["id"], fontsize=8, ha='right')

ax.set_title(f'Exits on {cluster["displayName"]}')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')

# Save the output image
output_filename = f"{cluster['displayName'].replace(' ', '_')}_Exits.png"
output_path = os.path.join(base_image_dir, output_filename)
plt.savefig(output_path)
plt.show()