import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

# Assuming you have temperature data for each county in California as a dictionary where the keys are county names.
# Replace this with your actual temperature data.
temperature_data = {
    'Imperial': 73.11,
    'Riverside': 70.28,
    'San Bernardino': 66.90,
    'Orange': 64.55,
    'Los Angeles': 64.15,
    'Kings': 63.64,
    'Merced': 62.86,
    'Sacramento': 62.21,
    'Stanislaus': 62.06,
    'Kern': 61.51,
    'Sutter': 61.47,
    'San Joaquin': 61.45,
    'Fresno': 61.45,
    'San Diego': 61.39,
    'Ventura': 61.17,
    'Yolo': 60.94,
    'Tehama': 60.88,
    'Glenn': 60.81,
    'Calaveras': 60.63,
    'Solano': 60.44,
    'Tulare': 60.40,
    'Colusa': 60.40,
    'Butte': 60.08,
    'Yuba': 60.07,
    'Contra Costa': 60.05,
    'Amador': 59.74,
    'Santa Barbara': 59.65,
    'Santa Clara': 59.65,
    'San Luis Obispo': 59.58,
    'Napa': 59.39,
    'Alameda': 59.21,
    'Lake': 58.57,
    'Santa Cruz': 58.50,
    'Inyo': 58.03,
    'Marin': 57.97,
    'Sonoma': 57.89,
    'San Benito': 57.80,
    'Monterey': 57.65,
    'San Mateo': 57.38,
    'San Francisco': 57.37,
    'Madera': 56.68,
    'El Dorado': 56.38,
    'Mendocino': 55.93,
    'Mariposa': 55.83,
    'Shasta': 55.47,
    'Nevada': 55.31,
    'Trinity': 54.93,
    'Placer': 54.09,
    'Humboldt': 54.04,
    'Del Norte': 53.38,
    'Tuolumne': 53.29,
    'Siskiyou': 50.53,
    'Sierra': 49.97,
    'Mono': 48.98,
    'Lassen': 48.35,
    'Plumas': 48.26,
    'Modoc': 47.78,
    'Alpine': 44.35
}

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")

# Merge temperature data with the california_data GeoDataFrame
california_data['Temperature'] = california_data['NAME'].map(temperature_data)

# Specify the colormap and the data range
cmap = 'hot_r'
vmin = min(temperature_data.values())
vmax = max(temperature_data.values())

fig, ax = plt.subplots(figsize=(10, 10))

# Plot California counties data with the temperature heatmap
california_data.plot(ax=ax, column='Temperature', cmap=cmap, edgecolor='black', linewidth=0.5, legend=True, vmin=vmin, vmax=vmax)

# Plot filtered wildfires that fall within California
california_data.plot(ax=ax, color='white', alpha=0.4)

ax.set_title("California Counties - Temperature Heatmap")
plt.show()
