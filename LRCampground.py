import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from shapely.geometry import Polygon
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def distanceBetween (point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

print("starting to read files")

california_data = gpd.read_file("./testData/CA_Counties_TIGER2016.geojson")
campground_data = gpd.read_file("./testData/Campground Sites.geojson")
wildfire_data = gpd.read_file("./testData/California_Fire_Perimeters_(all).geojson")

# Reproject the wildfire data to match the CRS of California counties data
campground_data_reprojected = campground_data.to_crs(california_data.crs)
wildfire_data = wildfire_data.to_crs(california_data.crs)

campgrounds_in_california = gpd.sjoin(campground_data_reprojected, california_data, op="within")
wildfires_in_california = gpd.sjoin(wildfire_data, california_data, op="within")

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


print("gaussian distrubition getting ...")

wildfire_data['centroid'] = wildfire_data.geometry.centroid
wildfire_coords = np.column_stack((wildfire_data['centroid'].x, wildfire_data['centroid'].y))
kde = gaussian_kde(wildfire_coords.T)

print("getting fishnet information like distance and probability ...")

fishnet = gpd.GeoDataFrame({'geometry': grid_polygons}, crs=california_data.crs)

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

    distance = 10000000000000
    for campground in campground_coordinates:
        distance = min(distance, distanceBetween([centroid_x, centroid_y], campground))
        if distance == 0:
            break
    fishnet_distance.append(distance)
    print(distance)


fishnet['distance'] = fishnet_distance
fishnet['probability'] = wildfire_probability

print("machine learning training ...")

X = fishnet['distance'].values.reshape(-1, 1)  # Convert to 2D array
y = fishnet['probability']  # Replace 'probability' with the column name of your target variableX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("Mean Squared Error:", mse)
print("R-squared:", r2)

fishnet['predicted_probability'] = model.predict(X)
print(fishnet.head())
print(fishnet['predicted_probability'].describe())

print("plotting ...")

cmap = plt.get_cmap('inferno')
norm = plt.Normalize(vmin=np.min(fishnet['predicted_probability']), vmax=np.max(fishnet['predicted_probability']))

fig, ax = plt.subplots(figsize=(10, 10))
california_data.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5, alpha=1, zorder=1)
fishnet.boundary.plot(ax=ax, facecolor=cmap(norm(fishnet['predicted_probability'])), edgecolor='black', linewidth=0.5)


ax.set_title("LR on knn neighbor")

plt.show()
