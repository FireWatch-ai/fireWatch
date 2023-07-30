library(datasets)  # Load base packages manually

# Installs pacman ("package manager") if needed
if (!require("pacman")) install.packages("pacman")

# Use pacman to load add-on packages as desired
pacman::p_load(pacman, caret, lars, tidyverse,sf,RSocrata,viridis,spatstat,spdep,gridExtra, spatialreg)

options(scipen=9999)

library(tidyverse)
library(sf)
library(RSocrata)
library(spatstat)
library(viridis)
library(FNN)
library(spdep)
library(gridExtra)

source("https://raw.githubusercontent.com/urbanSpatial/Public-Policy-Analytics-Landing/master/functions.r")

nhoods <-
  st_read("https://data.sfgov.org/api/geospatial/p5b7-5n3h?method=export&format=GeoJSON") %>%
  st_transform('ESRI:102642') %>%
  st_buffer(-1) #to correct some of the digitization errors
  

bound <-
  st_read("C:/Users/vinod/Desktop/City_Boundaries.geojson") %>%
  st_transform(st_crs(nhoods)) %>%
  filter(OBJECTID == 370)

str <- st_read("https://data.sfgov.org/api/geospatial/3psu-pn9h?method=export&format=GeoJSON")
main_streets <- filter(str, street %in% c("MARKET","PORTOLA"))

fishnet <-
  st_make_grid(nhoods, cellsize = 500) %>%
  st_sf() %>%
  mutate(uniqueID = rownames(.)) %>%
  .[bound,] #return only grid cells in the San Fran boundary

ggplot() +
  geom_sf(data=fishnet) +
  geom_sf(data=bound, fill=NA) +
  labs(title="San Francisco & Fishnet") +
  mapTheme()

fires <-
  read.socrata("https://data.sfgov.org/Public-Safety/Fire-Incidents/wr8u-xric?Primary Situation=111 Building fire") %>%
  mutate(year = substr(incident_date,1,4)) %>%
  filter(year >= 2017) %>%
  st_as_sf(wkt="point") %>%
  st_set_crs(4326) %>%
  st_transform(st_crs(nhoods)) %>%
  dplyr::select(year) %>%
  .[nhoods,]

ggplot() +
  geom_sf(data=nhoods) +
  geom_sf(data=main_streets, colour="white", size=2) +
  geom_sf(data=fires) +
  labs(title="Building fires, San Francisco: 2017 - 2021",
       subtitle="Market Street in white") +
  mapTheme()

fires17_20 <- filter(fires, year < 2021)
fires21 <- filter(fires, year == 2021)

fire_ppp <- as.ppp(st_coordinates(fires17_20), W = st_bbox(nhoods))
fire_KD <- density.ppp(fire_ppp, 1000)

as.data.frame(fire_KD) %>%
  st_as_sf(coords = c("x", "y"), crs = st_crs(nhoods)) %>%
  aggregate(., fishnet, mean) %>%
  ggplot() +
  geom_sf(aes(fill=value)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(name = "Density",
                     option = "magma") +
  labs(title = "Kernel density risk of fires",
       subtitle = "Market St. overlayed") +
  mapTheme()    

fire_net <-
  dplyr::select(fires17_20) %>%
  mutate(countFires = 1) %>%
  aggregate(., fishnet, sum) %>%
  mutate(countFires = replace_na(countFires, 0),
         uniqueID = rownames(.),
         cvID = sample(round(nrow(fishnet) / 24), size=nrow(fishnet), replace = TRUE))

ggplot() +
  geom_sf(data = fire_net, aes(fill = countFires)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma",
                     name="Fire Count") +
  labs(title = "Count of fires for the fishnet",
       subtitle = "Market St. in white") +
  mapTheme()

landUse <- st_read("https://data.sfgov.org/api/geospatial/us3s-fp9q?method=export&format=GeoJSON") %>%
  filter(bldgsqft > 0) %>%
  filter(yrbuilt < 2022 & yrbuilt > 1900) %>%
  mutate(yrbuilt = as.numeric(yrbuilt), bldgsqft = as.numeric(bldgsqft)) %>%
  st_transform(st_crs(nhoods))

vacant <-
  filter(landUse, landuse == "VACANT") %>%
  st_centroid()

vars_net <-
  cbind(st_drop_geometry(fishnet),
        dplyr::select(vacant) %>%
          mutate(countVacants = 1) %>%
          aggregate(., fishnet, sum) %>%
          mutate(countVacants = replace_na(countVacants, 0))) %>%
  st_sf()

ggplot() +
  geom_sf(data = vars_net, aes(fill = countVacants)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma",
                     name="Vacant Count") +
  labs(title = "Count of vacants for the fishnet",
       subtitle = "Market St. in white") +
  mapTheme()

st_c <- st_coordinates
st_coid <- st_centroid

vars_net <-
  vars_net %>%
  mutate(
    vacants.nn =
      nn_function(st_c(st_coid(vars_net)), st_c(vacant),3))

head(vars_net)

ggplot() +
  geom_sf(data = vars_net, aes(fill = vacants.nn)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma", direction = -1,
                     name="Vacant Distance") +
  labs(title = "Nearest neighbor distance to vacants",
       subtitle = "Market St.in white") +
  mapTheme()

vars_net <-
  cbind(st_drop_geometry(vars_net),
        st_centroid(landUse) %>%
          dplyr::select(yrbuilt, bldgsqft) %>%
          aggregate(., fishnet, mean) %>%
          mutate(yrbuilt = replace_na(yrbuilt, 0),
                 bldgsqft = replace_na(bldgsqft, 0))) %>%
  st_sf()

ggplot() +
  geom_sf(data=filter(vars_net, yrbuilt >= 1900), aes(fill = yrbuilt)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma",
                     name="Year") +
  labs(title = "Mean year built of parcels",
       subtitle = "Market St. in white") +
  mapTheme()

graf <-
  read.socrata("https://data.sfgov.org/resource/vw6y-z8j6.json?$limit=5000&Category=Graffiti") %>%
  st_as_sf(coords = c("point.longitude", "point.latitude"), crs = 4326, agr = "constant") %>%
  st_transform(st_crs(nhoods)) %>%
  dplyr::select(requested_datetime) %>%
  .[nhoods,]

ggplot() +
  geom_sf(data = vars_net) +
  geom_sf(data=graf, size=.5) +
  labs(title = "Random sample of 311 graffiti points") +
  mapTheme()   

vars_net <-
  vars_net %>%
  mutate(
    graf.nn =
      nn_function(st_c(st_coid(vars_net)), st_c(graf),5))

ggplot() +
  geom_sf(data = vars_net, aes(fill = graf.nn)) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma", direction = -1,
                     name="Vacant Distance") +
  labs(title = "Nearest neighbor distance to graffiti reports",
       subtitle = "Market St. in white") +
  mapTheme()

final_net <-
  left_join(fire_net, st_drop_geometry(vars_net), by="uniqueID") %>%
  filter(yrbuilt > 1900)

final_net <-
  st_centroid(final_net) %>%
  st_join(nhoods) %>%
  st_drop_geometry() %>%
  left_join(dplyr::select(final_net, geometry, uniqueID)) %>%
  st_sf() %>%
  na.omit()

ggplot() +
  geom_sf(data = final_net, aes(fill = nhood), show.legend=FALSE) +
  geom_sf(data=main_streets, colour="white", size=1) +
  scale_fill_viridis(option = "magma", discrete = T,
                     name="Vacant Count") +
  labs(title = "Neighborhoods joined to the fishnet",
       subtitle = "Market St. in white") +
  mapTheme()

)




