import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from shapely.geometry import Polygon

import matplotlib.colors as mcolors

def rgba_to_color_name(rgba_tuple):
    color = mcolors.to_rgba(rgba_tuple)
    color_name = mcolors.to_color(color)
    return color_name

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")

# Check the CRS of both datasets
print(california_data.crs)
print(wildfire_data.crs)

# Reproject wildfire_data to a projected CRS
# Replace 'EPSG:4326' with the appropriate CRS code for your data if needed.
wildfire_data = wildfire_data.to_crs(california_data.crs)

print("starting gaussian kernel density estimation ...")
# Convert polygon/multipolygon geometries to their centroids (representative points)
wildfire_data['centroid'] = wildfire_data.geometry.centroid

# Extract coordinates of the representative points (centroids) and stack them into a 2D array.
wildfire_coords = np.column_stack((wildfire_data['centroid'].x, wildfire_data['centroid'].y))

# Perform kernel density estimation on the wildfire coordinates.
kde = gaussian_kde(wildfire_coords.T)

# Create a grid of points covering the extent of California counties.
xmin, ymin, xmax, ymax = california_data.total_bounds
x, y = np.mgrid[xmin:xmax:300j, ymin:ymax:300j]
grid_coords = np.column_stack((x.ravel(), y.ravel()))

# Evaluate the KDE on the grid points.
density_values = kde(grid_coords.T).reshape(x.shape)
# Calculate the bounding box for California counties
bbox = california_data.total_bounds

print("checking fishnet")

# Create a fishnet grid with smaller cells covering the bounding box of California counties
cell_size = 25000  # Cell size in meters (25 km = 25000 meters)
rows = int((bbox[3] - bbox[1]) / cell_size)
cols = int((bbox[2] - bbox[0]) / cell_size)

# Generate polygons for each cell in the fishnet
grid_polygons = []
for x in range(cols):
    for y in range(rows):
        xmin = bbox[0] + x * cell_size
        xmax = bbox[0] + (x + 1) * cell_size
        ymin = bbox[1] + y * cell_size
        ymax = bbox[1] + (y + 1) * cell_size

        # Clip the fishnet cell to the extent of California
        clipped_polygon = Polygon([(max(xmin, bbox[0]), max(ymin, bbox[1])),
                                   (min(xmax, bbox[2]), max(ymin, bbox[1])),
                                   (min(xmax, bbox[2]), min(ymax, bbox[3])),
                                   (max(xmin, bbox[0]), min(ymax, bbox[3]))])
        interscting_california = california_data[california_data.intersects(clipped_polygon)]
        if not interscting_california.empty:
            grid_polygons.append(clipped_polygon)

fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)




print("getting fishnet colors ...")
fishnet_colors = []
# Calculate the kernel density value at the centroid of each fishnet cell and store the corresponding color
for cell_polygon in grid_polygons:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y
    density_value = kde([centroid_x, centroid_y])
    fishnet_colors.append(density_value)

cmap = plt.get_cmap('inferno')
norm = plt.Normalize(vmin=np.min(fishnet_colors), vmax=np.max(fishnet_colors))

fishnet['color'] = fishnet_colors

for cell_polygon in grid_polygons:
    print(norm(cell_polygon['color']))
    print(cmap(norm(cell_polygon['color'])))

fig, ax = plt.subplots(figsize=(10, 10))

print("plotting")
# Plot California counties data on top of the heatmap.
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5, alpha=1, zorder=1)

# Plot the heatmap using the density values on top of the California map.
fishnet.boundary.plot(ax=ax, facecolor=rgba_to_color_name(cmap(norm(fishnet['color']))), edgecolor='black',linewidth=0.5)


ax.set_title("Kernel Density Estimation Heatmap of Wildfires in California with Fishnet")
plt.show()
