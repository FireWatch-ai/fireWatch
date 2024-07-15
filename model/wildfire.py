import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
import numpy as np
import random as rnd

diffusion = 8.2
wood_burn_constant = 20.0
temperature_engery_gain = 135
environmental_temperature = 300.0
combustion_temperautre = 530.0
k_1 = 0.12
points = 200
length = 400
dx = length / points * 1.
h = 0.1
time = 100


def wildfire():
  temperature_old = np.ones((points, points)) * environmental_temperature
  wood_old = np.ones((points, points))
  for i in range(points):
    for j in range(points):
      temperature_old[i, j] = environmental_temperature
      # if(i > 75 and i < 90 and j > 75 and j < 90):
        # temperature_old[i, j] = 1200.0
      # simulate lighting strike
      if(i > 80 and i < 84 and j > 80 and j < 84):
        temperature_old[i, j] = 28033.15
      wood_old[i, j] = math.exp(-0.001 * ((i - 100) ** 2 + (j - 100) ** 2))*20
      wood_old[i, j] += math.exp(-0.0005 * ((i - 50) ** 2 + (j - 50) ** 2))*20
      wood_old[i, j] += math.exp(-0.0005 * ((i - 100) ** 2 + (j - 50) ** 2))*20

  temperature_new = np.ones((points, points)) * environmental_temperature
  wood_new = np.ones((points, points))

  num_of_iterations = 100/h
  for t in range(int(num_of_iterations)):
    for i in range(1, points - 1):
      for j in range(1, points - 1):
          wood_new[i, j] = wood_old[i, j]
          temperature_new[i, j] = temperature_old[i, j]+ h*diffusion*(1/dx**2)*(temperature_old[i+1, j]
                                   + temperature_old[i-1, j] + temperature_old[i,j+1]
                                   + temperature_old[i,j-1] - 4*temperature_old[i,j]) + h*k_1*(
                                     environmental_temperature - temperature_old[i,j])
          if temperature_old[i, j] > combustion_temperautre:
            wood_new[i, j] = wood_old[i, j] - h*(wood_old[i, j] /wood_burn_constant)
            temperature_new[i, j] += h*temperature_engery_gain*(wood_old[i, j] /wood_burn_constant)
    temperature_old = temperature_new
    wood_old = wood_new

    time = str(round(t*h,2))


    plt.subplot(1, 2, 1)
    plt.imshow(temperature_new, cmap='hot', interpolation='nearest', vmin=combustion_temperautre, vmax=1200.0)
    plt.gca().invert_yaxis()
    plt.xlabel('x-coordinate')
    plt.ylabel('y-coordinate')
    plt.title('Temperature at t =' + time + " seconds")
    plt.subplot(1, 2, 2)
    plt.colorbar(label='Temperature - Kelvin')
    plt.imshow(wood_new, cmap='Greens', interpolation='nearest', vmin=0, vmax=30.0)
    plt.xlabel('x-coordinate')
    plt.ylabel('y-coordinate')
    plt.gca().invert_yaxis()
    plt.title('Wood at t = ' + time + " seconds")
    plt.colorbar(label="Fuel kg per meter squared")
    plt.draw()
    plt.pause(0.01)
    plt.clf()

wildfire()
