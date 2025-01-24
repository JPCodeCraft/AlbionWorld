import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider

# Load the JSON data
with open('albionLocations.json', 'r') as f:
    data = json.load(f)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Configure color mapping for different location types
color_map = {
    # Arena types (Purples)
    "ARENA_CRYSTAL": "#9B59B6",
    "ARENA_CRYSTAL_20VS20": "#8E44AD",
    "ARENA_CRYSTAL_NONLETHAL": "#BB8FCE",
    "ARENA_CUSTOM": "#6C3483",
    "ARENA_STANDARD": "#A569BD",
    
    # Dungeon types (Reds/Yellows)
    "CORRUPTED_DUNGEON_INTERMEDIATE": "#4A235A",
    "DUNGEON_BLACK_1": "#2F2F2F",
    "DUNGEON_BLACK_2": "#3F3F3F",
    "DUNGEON_BLACK_3": "#4F4F4F",
    "DUNGEON_BLACK_4": "#5F5F5F",
    "DUNGEON_BLACK_5": "#6F6F6F",
    "DUNGEON_BLACK_6": "#7F7F7F",
    "DUNGEON_HELL_10V10_LETHAL": "#FF0000",
    "DUNGEON_HELL_10V10_NON_LETHAL": "#FF6347",
    "DUNGEON_HELL_2V2_LETHAL": "#DC143C",
    "DUNGEON_HELL_2V2_NON_LETHAL": "#CD5C5C",
    "DUNGEON_HELL_5V5_LETHAL": "#B22222",
    "DUNGEON_HELL_5V5_NON_LETHAL": "#E9967A",
    "DUNGEON_RED": "#FF4500",
    "DUNGEON_SAFEAREA": "#98FB98",
    "DUNGEON_YELLOW": "#FFD700",
    
    # Guild/Player Areas (Blues/Greens)
    "GUILDISLAND": "#3498DB",
    "PLAYERISLAND": "#2ECC71",
    
    # Expeditions (Greens by tier)
    "HARDCORE_EXPEDITION_STANDARD": "#228B22",
    "HARDCORE_EXPEDITION_SURFACE": "#32CD32",
    "T3_EXPEDITION_STANDARD": "#ADFF2F",
    "T4_EXPEDITION_STANDARD": "#7CFC00",
    "T4_EXPEDITION_SURFACE": "#00FF00",
    "T5_EXPEDITION_STANDARD": "#32CD32",
    "T5_EXPEDITION_SURFACE": "#008000",
    "T6_EXPEDITION_STANDARD": "#006400",
    "T6_EXPEDITION_SURFACE": "#004d00",
    
    # Cities/Safe Areas (Light colors)
    "HIDEOUT": "#228B22",
    "PLAYERCITY_BLACK": "#2F4F4F",
    "PLAYERCITY_BLACK_NOFURNITURE": "#3B5998",
    "PLAYERCITY_BLACK_PORTALCITY_NOFURNITURE": "#483D8B",
    "PLAYERCITY_BLACK_REST": "#2F4F4F",
    "PLAYERCITY_BLACK_ROYAL": "#4B0082",
    "PLAYERCITY_BLACK_ROYAL_NOFURNITURE": "#6A5ACD",
    "PLAYERCITY_BLACK_ROYAL_NOFURNITURE_HALL_OF_FAME": "#7B68EE",
    "PLAYERCITY_BLACK_SMUGGLERSDEN": "#8A2BE2",
    "PLAYERCITY_SAFEAREA_01": "#98FB98",
    "PLAYERCITY_SAFEAREA_02": "#90EE90",
    "PLAYERCITY_SAFEAREA_NOFURNITURE": "#00FA9A",
    "SAFEAREA": "#F0FFF0",
    "STARTAREA": "#F5FFFA",
    "STARTINGCITY": "#F0F8FF",
    
    # Open PvP (Strong colors)
    "OPENPVP_BLACK_1": "#1A1A1A",
    "OPENPVP_BLACK_2": "#2A2A2A",
    "OPENPVP_BLACK_3": "#3A3A3A",
    "OPENPVP_BLACK_4": "#4A4A4A",
    "OPENPVP_BLACK_5": "#5A5A5A",
    "OPENPVP_BLACK_6": "#6A6A6A",
    "OPENPVP_RED": "#8B0000",
    "OPENPVP_YELLOW": "#FFD700",
    
    # Tunnels/Passages (Browns/Grays)
    "PASSAGE_BLACK": "#696969",
    "PASSAGE_RED": "#8B4513",
    "TUNNEL_BLACK_HIGH": "#2F4F4F",
    "TUNNEL_BLACK_LOW": "#708090",
    "TUNNEL_BLACK_MEDIUM": "#5F9EA0",
    "TUNNEL_DEEP": "#654321",
    "TUNNEL_DEEP_RAID": "#8B4513",
    "TUNNEL_HIDEOUT": "#556B2F",
    "TUNNEL_HIDEOUT_DEEP": "#6B8E23",
    "TUNNEL_HIGH": "#A0522D",
    "TUNNEL_LOW": "#DEB887",
    "TUNNEL_MEDIUM": "#CD853F",
    "TUNNEL_ROYAL": "#4B0082",
    "TUNNEL_ROYAL_RED": "#800000",
    
    # Special/Misc
    "DEBUG_BLACK": "#000000",
    "TUTORIAL": "#87CEEB"
}

# Lists to track all coordinates for setting plot limits
all_x = []
all_y = []

# Plot each location with valid worldmapposition
for location in data:
    world_map_pos = location.get('worldmapposition')
    if world_map_pos is None:
        continue  # Skip entries with null worldmapposition
        
    if 'size' not in location:
        print(f"Skipping {location.get('id')} - missing size")
        continue

    try:
        # Extract position and size
        x, y = world_map_pos
        width, height = location['size']
        #divite size by 100
        width = width / 100
        height = height / 100
        loc_type = location.get('type', 'UNKNOWN')
        display_name = location.get('displayName', 'No Name')
        
        # Update coordinate tracking
        all_x.extend([x, x + width])
        all_y.extend([y, y + height])
        
        # Create rectangle patch
        color = color_map.get(loc_type, 'gray')
        rect = patches.Rectangle(
            (x, y), width, height,
            linewidth=1, edgecolor=color,
            facecolor=color, alpha=0.3,
            label=loc_type
        )
        
        # Add rectangle to plot
        ax.add_patch(rect)
        
        # Add text label at center
        ax.text(
            x + width/2, y + height/2,
            display_name,
            fontsize=6, ha='center', va='center',
            color='black', alpha=0.7
        )
        
    except (ValueError, TypeError) as e:
        print(f"Skipping {location.get('id')} - invalid data: {e}")

# Set plot limits and aspect ratio if valid locations were found
if all_x and all_y:
    ax.set_xlim(min(all_x), max(all_x))
    ax.set_ylim(min(all_y), max(all_y))
    ax.set_aspect('equal')
else:
    print("No valid locations with worldmapposition found!")
    plt.close()
    exit()

ax.grid(True, linestyle='--', alpha=0.5)
ax.set_title('Albion World Map Locations')
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')

# Create legend
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))  # Remove duplicates
ax.legend(unique_labels.values(), unique_labels.keys(), 
          title='Location Types', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add zoom functionality
def zoom_factory(ax, base_scale=2.):
    def zoom(event):
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        ax.figure.canvas.draw()

    fig.canvas.mpl_connect('scroll_event', zoom)

zoom_factory(ax)

plt.tight_layout()
plt.show()