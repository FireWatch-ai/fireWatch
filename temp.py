import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from shapely.geometry import Polygon
from apiExperiment import temp

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")


print("fishnet stage 1 loading ...")

bbox = california_data.total_bounds

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
fishnet.to_crs(epsg=4326, inplace=True)

for cell_polygon in fishnet['geometry']:
    centroid = cell_polygon.centroid
    latitude, longitude = centroid.y, centroid.x  # Note that y is latitude and x is longitude

    new_temp = temp(latitude, longitude)
    print(new_temp.temperature)
    temperature_data.append(new_temp.temperature[1])

fishnet['temperature'] = temperature_data

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

print("plotting now ...")

cmap = plt.get_cmap('hot_r')
norm = plt.Normalize(vmin=np.min(temperature_data), vmax=np.max(temperature_data))

# Plot fishnet on top of the map, filling cells with red color
fishnet.plot(ax=ax, facecolor=cmap(norm(fishnet['temperature'])),edgecolor='blue', linewidth=0.1)

ax.set_title("Wildfires Overlayed on California Counties with Smaller Fishnet")
plt.show()

