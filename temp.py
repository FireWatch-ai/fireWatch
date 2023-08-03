import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from shapely.geometry import Polygon
from apiExperiment import temp

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")



bbox = california_data.total_bounds
print(bbox)

print("fishnet stage 1 loading ...")
# Create a fishnet grid with smaller cells covering the bounding box of California counties
cell_size = 50000  # Cell size in meters (25 km = 25000 meters)
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


temperature_data = []
for cell_polygon in grid_polygons:
    new_temp = temp(cell_polygon.centroid.x, cell_polygon.centroid.y)
    print(new_temp.temperature)
    temperature_data.append(new_temp.temperature[1])
    

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

print("plotting now ...")

# Plot California counties data with the temperature heatmap
california_data.plot(ax=ax, column='Temperature', cmap=cmap, edgecolor='black', linewidth=0.5, legend=True, vmin=vmin, vmax=vmax)


# Plot fishnet on top of the map, filling cells with red color
fishnet.plot(ax=ax,  edgecolor='blue', linewidth=0.1)

ax.set_title("Wildfires Overlayed on California Counties with Smaller Fishnet")
plt.show()

