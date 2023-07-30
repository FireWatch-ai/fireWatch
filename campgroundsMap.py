import geopandas as gpd
import matplotlib.pyplot as plt

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")

# Check the CRS of both datasets
print(california_data.crs)
print(campground_data.crs)

# Reproject the wildfire data to match the CRS of California counties data
campground_data_reprojected = campground_data.to_crs(california_data.crs)

# Perform a spatial join to associate wildfires with California counties
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")

fig, ax = plt.subplots(figsize=(10, 10))

# Plot California counties data
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=0.5)

# Plot filtered wildfires that fall within California
campgrounds_in_california.plot(ax=ax, color='green', alpha=0.7)

ax.set_title("Campgrounds Overlayed on California Counties")
plt.show()
