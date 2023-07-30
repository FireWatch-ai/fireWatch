import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")

# Check the CRS of both datasets
print(california_data.crs)
print(wildfire_data.crs)

# Reproject wildfire_data to a projected CRS
# Replace 'EPSG:4326' with the appropriate CRS code for your data if needed.
wildfire_data = wildfire_data.to_crs('EPSG:3395')

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

fig, ax = plt.subplots(figsize=(10, 10))

# Plot California counties data on top of the heatmap.
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5, alpha=1, zorder=1)
# Plot the heatmap using the density values on top of the California map.
ax.imshow(density_values.T, origin='lower', extent=[xmin, xmax, ymin, ymax], cmap='inferno', alpha=0.8, zorder=2)

ax.set_title("Kernel Density Estimation Heatmap of Wildfires in California")
plt.show()
