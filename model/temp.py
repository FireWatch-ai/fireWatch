import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from shapely.geometry import Polygon
from shapely.geometry import Point
from weatherApi import temp

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")

print("fishnet stage 1 loading ...")

bbox = california_data.total_bounds
cell_size = 5000
rows = int((bbox[3] - bbox[1]) / cell_size)
cols = int((bbox[2] - bbox[0]) / cell_size)

grid_polygons = []
for x in range(cols):
    for y in range(rows):
        xmin = bbox[0] + x * cell_size
        xmax = bbox[0] + (x + 1) * cell_size
        ymin = bbox[1] + y * cell_size
        ymax = bbox[1] + (y + 1) * cell_size

        clipped_polygon = Polygon([(max(xmin, bbox[0]), max(ymin, bbox[1])),
                                   (min(xmax, bbox[2]), max(ymin, bbox[1])),
                                   (min(xmax, bbox[2]), min(ymax, bbox[3])),
                                   (max(xmin, bbox[0]), min(ymax, bbox[3]))])
        interscting_california = california_data[california_data.intersects(clipped_polygon)]
        if not interscting_california.empty:
            grid_polygons.append(clipped_polygon)

print("checking fishnet ...")

fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)

temperature_data = []
fishnet.to_crs(epsg=4326, inplace=True)
count = 0
for cell_polygon in fishnet['geometry']:
    centroid = cell_polygon.centroid
    latitude, longitude = centroid.y, centroid.x

    new_temp = temp(latitude, longitude)
    print(new_temp.temperature)
    temperature_data.append(new_temp.temperature[1])
    count += 1
    print(count)

print("done")

fishnet['temperature'] = temperature_data
cmap = plt.get_cmap('hot_r')
norm = plt.Normalize(vmin=np.min(temperature_data), vmax=np.max(temperature_data))
fishnet = fishnet.to_crs(california_data.crs)

print("plotting now ...")

fig, ax = plt.subplots(figsize=(10, 10))

california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5, alpha=1, zorder=1)
fishnet.boundary.plot(ax=ax, facecolor=cmap(norm(fishnet['temperature'])),edgecolor='blue', linewidth=0.1)

cax = plt.axes([0.85, 0.2, 0.02, 0.6])  
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label('Temperature in California')

ax.set_title("Wildfires Overlayed on California Counties with Smaller Fishnet")
plt.show()

