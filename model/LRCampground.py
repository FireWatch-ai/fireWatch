import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from shapely.geometry import Point, Polygon
from weatherApi import temp

def distance_between(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

print("Starting to read files")

# Read GeoJSON files
california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")
wildfire_data_new = gpd.read_file("./testData/NIFC_2023_Wildfire_Perimeters.geojson")

# Reproject the wildfire data to match the CRS of California counties data
campground_data_reprojected = campground_data.to_crs(california_data.crs)
wildfire_data_reprojected = wildfire_data.to_crs(california_data.crs)
wildfire_data_new_reprojected = wildfire_data_new.to_crs(california_data.crs)

# Spatial joins
campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")
wildfires_in_california = gpd.sjoin(wildfire_data_reprojected, california_data, op="within")
wildfires_in_california_new = gpd.sjoin(wildfire_data_new_reprojected, california_data, op="within")

print("Creating grid polygons ...")

# Create grid polygons
bbox = california_data.total_bounds
cell_size = 100000
rows = int((bbox[3] - bbox[1]) / cell_size)
cols = int((bbox[2] - bbox[0]) / cell_size)

grid_polygons = []
for x in range(cols):
    for y in range(rows):
        xmin = bbox[0] + x * cell_size
        xmax = bbox[0] + (x + 1) * cell_size
        ymin = bbox[1] + y * cell_size
        ymax = bbox[1] + (y + 1) * cell_size

        clipped_polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])
        intersecting_california = california_data[california_data.intersects(clipped_polygon)]
        if not intersecting_california.empty:
            grid_polygons.append(clipped_polygon)

fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)

print("Calculating wildfire probability and temperature ...")

# Calculate wildfire probability and temperature
wildfire_data_reprojected['centroid'] = wildfire_data_reprojected.geometry.centroid
wildfire_coords = np.column_stack((wildfire_data_reprojected['centroid'].x, wildfire_data_reprojected['centroid'].y))
kde = gaussian_kde(wildfire_coords.T)

temperature_data = []
fishnet.to_crs(epsg=4326, inplace=True)
count = 0
for cell_polygon in fishnet['geometry']:
    centroid = cell_polygon.centroid
    latitude, longitude = centroid.y, centroid.x  # Note that y is latitude and x is longitude

    new_temp = temp(latitude, longitude)
    print(new_temp.temperature)
    temperature_data.append(new_temp.temperature[1])
    count += 1
    print(count)

print("done temp")

print("Performing spatial analysis ...")
fishnet['temperature'] = temperature_data
fishnet = fishnet.to_crs(california_data.crs)

campground_coordinates = []

for cell_polygon in fishnet['geometry']:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y

    intersecting_campgrounds = campgrounds_in_california[campgrounds_in_california.intersects(cell_polygon)]
    if not intersecting_campgrounds.empty:
        campground_coordinates.append([centroid_x, centroid_y])


fishnet_distance = []
wildfire_probability = []

for cell_polygon in grid_polygons:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y
    density_value = kde([centroid_x, centroid_y])[0]
    wildfire_probability.append(density_value)
    #set distance to largest possible value
    distance = 1000000000000000000000

    for campground in campground_coordinates:
        if distance_between([centroid_x, centroid_y], campground) < distance:
            distance = distance_between([centroid_x, centroid_y], campground)
    fishnet_distance.append(distance)

fishnet['distance'] = fishnet_distance
fishnet['probability'] = wildfire_probability

print("Performing machine learning training ...")

X = fishnet[['distance', 'temperature']].values
y = fishnet['probability']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05    , random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("Mean Squared Error:", mse)
print("R-squared:", r2)

fishnet['predicted_probability'] = model.predict(X)

print(fishnet.head())

print("Plotting ...")

cmap = plt.get_cmap('inferno')
norm = plt.Normalize(vmin=np.min(fishnet['predicted_probability']), vmax=np.max(fishnet['predicted_probability']))

colors = []

for cell_polygon in fishnet['geometry']:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y

    intersecting_wildfires = wildfires_in_california_new[wildfires_in_california_new.intersects(cell_polygon)]

    if not intersecting_wildfires.empty:
        colors.append('red')
    else:
        colors.append(cmap(norm(cell_polygon['predicted_probability'])))
fishnet['color'] = colors


fig, ax = plt.subplots(figsize=(10, 10))
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5, alpha=1, zorder=1)
fishnet.boundary.plot(ax=ax,
                      facecolor=fishnet['color'],
                      edgecolor='black',
                      linewidth=0.5)

ax.set_title("LR on knn neighbor")

plt.show()
