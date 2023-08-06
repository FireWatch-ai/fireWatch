import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import numpy as np
from scipy.stats import gaussian_kde
from shapely.geometry import Polygon


def distanceBetween (point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")

campground_data_reprojected = campground_data.to_crs(california_data.crs)
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")

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

campground_coordinates = []

for cell_polygon in fishnet['geometry']:
    intersecting_campgrounds = campgrounds_in_california[campgrounds_in_california.intersects(cell_polygon)]
    if not intersecting_campgrounds.empty:
        campground_coordinates.append([cell_polygon.centroid.x, cell_polygon.centroid.y])

fishnet_distance = []
count = 0
for cell_polygon in grid_polygons:
    distance = 10000000000000
    for campground in campground_coordinates:
        distance = min(distance, distanceBetween([cell_polygon.centroid.x, cell_polygon.centroid.y], campground))
        if distance == 0:
            break
    fishnet_distance.append(distance)
    print(distance)
    count += 1
print(count)

fishnet['distance'] = fishnet_distance
cmap = plt.get_cmap('Greens_r')
norm = plt.Normalize(vmin=np.min(fishnet_distance), vmax=np.max(fishnet_distance))


print("plotting now ...")
fig, ax = plt.subplots(figsize=(10, 10))

california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)
fishnet.boundary.plot(ax=ax, facecolor=cmap(norm(fishnet['distance'])), edgecolor='black', linewidth=0.5)

cax = plt.axes([0.85, 0.2, 0.02, 0.6])  # [left, bottom, width, height]
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label('Distance to nearest campground')

ax.set_title("Knn of Campgrounds in California")
plt.show()




