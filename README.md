# fireWatch
Policy-based wildfire prevention. Currently in building out predictive model on using open source data in California. V.01 

# Initial fire plotting 

Here is the intial plotting of wildfires on california, alongside a guassian distrubition to create a probailbity, P from 0 < P < 1. 

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/wildfireInCalifornia.png)

![](https://github.com/blueishfiend692/fireWatch/blob/master/images/KDECalifornia.png)

# Factors mapping

Right now, we are testing 2 factors, 1 direct (temperature) and 1 neighbor (campgrounds). 

The get temperature we check the center of each fishnet and call on the weatherAPI, normailzing and assinging a color via cmap. This results in

![]



