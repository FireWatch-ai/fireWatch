import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")

print(california_data.crs)
print(campground_data.crs)

campground_data_reprojected = campground_data.to_crs(california_data.crs)
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")

bbox = california_data.total_bounds
print(bbox)

print("fishnet stage 1 loading ...")

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

fishnet_colors = []

for cell_polygon in fishnet['geometry']:
    intersecting_campgrounds = campgrounds_in_california[campgrounds_in_california.intersects(cell_polygon)]

    if not intersecting_campgrounds.empty:
        fishnet_colors.append('green')
    else:
        fishnet_colors.append('lightgrey')

fishnet['color'] = fishnet_colors

print("plotting now ...")

fig, ax = plt.subplots(figsize=(10, 10))

california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)

fishnet.plot(ax=ax, facecolor=fishnet['color'], edgecolor='blue', linewidth=0.1)

ax.set_title("Campgrounds Overlayed on California Counties with Smaller Fishnet")
plt.show()
