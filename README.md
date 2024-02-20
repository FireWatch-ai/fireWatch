# FireWatch

<p align="center">
  <img src="https://github.com/blueishfiend692/fireWatch/blob/master/images/fireWatch%20logo%20(1).gif?raw=true" alt="FireWatch Logo" width="400"/>
</p>

Policy-based wildfire prevention. Currently, we are in the process of building a predictive model using open-source data in California, combining multistage ML models. We hope to incorporate direct factors along with human factors, such as campgrounds, to effectively predict and manage wildfire resources. Version 1.0

# Initial fire plotting

Here is the initial plotting of wildfires in California, alongside a Gaussian distribution to create a probability, P, where 0 < P < 1.

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/wildfireInCalifornia.png)

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/KDECalifornia.png)

# Factors mapping

Right now, we are building the model using 2 factors: 1 direct (temperature) and 1 neighbouring (campgrounds).

To obtain temperature data, we check the center of each grid cell and call on the weather API.
```
temperature_data = []
fishnet.to_crs(epsg=4326, inplace=True)
...
for cell_polygon in fishnet['geometry']:
    centroid = cell_polygon.centroid
    latitude, longitude = centroid.y, centroid.x  # Note that y is latitude and x is longitude
    new_temp = temp(latitude, longitude)
    temperature_data.append(new_temp.temperature[1])
...
```

Normalizing and assigning a color via cmap.

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/TemperatureCalifornia.png)

For the campgrounds factor, the campground is plotted, and then the nearest distance is recorded and mapped via a cmap.

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/Campgrounds%20Map.png)

```
for cell_polygon in fishnet['geometry']:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y

    intersecting_campgrounds = campgrounds_in_california[campgrounds_in_california.intersects(cell_polygon)]
    if not intersecting_campgrounds.empty:
        campground_coordinates.append([centroid_x, centroid_y])

for cell_polygon in grid_polygons:
    centroid_x, centroid_y = cell_polygon.centroid.x, cell_polygon.centroid.y
    ...
    distance = max_number
    for campground in campground_coordinates:
        if distance_between([centroid_x, centroid_y], campground) < distance:
            distance = distance_between([centroid_x, centroid_y], campground)
    fishnet_distance.append(distance)

```

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/knn%20campgrounds.png)

# Local Moran

Applying a local Moran helps to reduce noise within the dataset.

```
w = libpysal.weights.Queen.from_dataframe(fishnet)
moran_loc_wildfire = Moran_Local(wildfire_probability, w, permutations=999)
fishnet['local_moran_wildfire'] = moran_loc_wildfire.Is

```

Here is the Moran overlayed with 2023 wildfires after training.

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/localMoranTest.png)

# Training

Using the kNN distance, logistic regression on temperature combined with the local Moran, a heatmap can be generated overlaying 2023 wildfires (not trained on) - achieving 74% accuracy on a 25000 square kilometer cell size.

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/V1.0TempCampground%26Moran%4065%25-5000px.png)
