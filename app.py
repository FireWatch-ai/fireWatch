import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")

# Check the CRS of both datasets
print(california_data.crs)
print(wildfire_data.crs)

# Reproject the wildfire data to match the CRS of California counties data
wildfire_data_reprojected = wildfire_data.to_crs(california_data.crs)

# Perform a spatial join to associate wildfires with California counties
wildfires_in_california = gpd.sjoin(wildfire_data_reprojected, california_data, op="within")

# Calculate the bounding box for California counties
bbox = california_data.total_bounds

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
        if clipped_polygon.within(california_data):
            grid_polygons.append(clipped_polygon)
        

# Create a GeoDataFrame from the grid polygons
fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))

# Plot California counties data
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)

# Plot filtered wildfires that fall within California
wildfires_in_california.plot(ax=ax, color='red', alpha=0.7)

# Plot fishnet on top of the map
fishnet.boundary.plot(ax=ax, color='blue', linewidth=0.5)

ax.set_title("Wildfires Overlayed on California Counties with Smaller Fishnet")
plt.show()
