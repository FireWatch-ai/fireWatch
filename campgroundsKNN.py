import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import numpy as np
from scipy.stats import gaussian_kde
from shapely.geometry import Polygon

# I want a kNN algorithm that will take each fishnet cell and find the nearest wildfire to it

# fundnction to find distance between two points
def distanceBetween (point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")

print(wildfire_data.crs)

# Check the CRS of both datasets
print(california_data.crs)
print(campground_data.crs)

# Reproject the wildfire data to match the CRS of California counties data
campground_data_reprojected = campground_data.to_crs(california_data.crs)

# Perform a spatial join to associate wildfires with California counties
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")

wildfire_data_reprojected = wildfire_data.to_crs(california_data.crs)

wildfires_in_california = gpd.sjoin(wildfire_data_reprojected, california_data, op="within")

# Calculate the bounding box for California counties
bbox = california_data.total_bounds
print(bbox)

print("fishnet stage 1 loading ...")
# Create a fishnet grid with smaller cells covering the bounding box of California counties
cell_size = 10000  # Cell size in meters (25 km = 25000 meters)
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

print("checking fishnet ...")
# Create a GeoDataFrame from the grid polygons
fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)

# Create a list to store the color for each fishnet cell


wildfire_coordinates = []

# Iterate through the fishnet cells and check if there's any wildfire inside
for cell_polygon in fishnet['geometry']:
    # Check if any wildfire intersects with the fishnet cell
    intersecting_campgrounds = campgrounds_in_california[campgrounds_in_california.intersects(cell_polygon)]
    intersecting_wildfires = wildfires_in_california[wildfires_in_california.intersects(cell_polygon)]

    if not intersecting_wildfires.empty:
        # If there are wildfires inside the cell, color it red
        wildfire_coordinates.append([cell_polygon.centroid.x, cell_polygon.centroid.y])


fishnet_distance = []

for cell_polygon in grid_polygons:
    distance = 10000000000000
    for wildfire in wildfire_coordinates:
        distance = min(distance, distanceBetween([cell_polygon.centroid.x, cell_polygon.centroid.y], wildfire))
    fishnet_distance.append(distance)
    print(distance)

fishnet['distance'] = fishnet_distance


cmap = plt.get_cmap('inferno_r')
norm = plt.Normalize(vmin=np.min(fishnet_distance), vmax=np.max(fishnet_distance))


# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

print("plotting now ...")

# Plot California counties data
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)

# Plot filtered wildfires that fall within California
campgrounds_in_california.plot(ax=ax, color='red', alpha=0.7)

# Plot fishnet on top of the map, filling cells with red color
fishnet.boundary.plot(ax=ax, facecolor=cmap(norm(fishnet['distance'])), edgecolor='black', linewidth=0.5)

ax.set_title("Campgrounds Overlayed on California Counties with Smaller Fishnet")
plt.show()





