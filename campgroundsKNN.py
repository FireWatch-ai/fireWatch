import geopandas as gpd
import matplotlib.pyplot as plt

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")

# Check the CRS of both datasets
print(california_data.crs)
print(campground_data.crs)

# Reproject the campground data to match the CRS of California counties data
campground_data_reprojected = campground_data.to_crs(california_data.crs)

# Perform a spatial join to associate campgrounds with California counties
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")

# Create a fishnet/grid covering the extent of California
minx, miny, maxx, maxy = california_data.total_bounds
cell_size = 0.05  # Adjust the cell size as needed
grid = gpd.GeoDataFrame.from_features(
    [
        {
            'geometry': box(x, y, x+cell_size, y+cell_size),
            'id': f"{x}_{y}"
        }
        for x in range(int(minx), int(maxx), int(cell_size*1000))
        for y in range(int(miny), int(maxy), int(cell_size*1000))
    ],
    crs=california_data.crs
)

# Clip the fishnet/grid to the boundary of California
grid_clipped = gpd.clip(grid, california_data)

# Plotting the map
fig, ax = plt.subplots(figsize=(10, 10))

# Plot California counties data
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)

# Plot filtered campgrounds that fall within California
campgrounds_in_california.plot(ax=ax, color='green', alpha=0.7)

# Plot the clipped fishnet/grid overlay
grid_clipped.boundary.plot(ax=ax, color='blue', linewidth=0.3)

ax.set_title("Campgrounds Overlayed on California Counties with Fishnet Grid")
plt.show()
