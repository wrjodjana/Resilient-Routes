import numpy as np

# Constants from transform.py
x_min, x_max = -70.784213, -71.600974   # Adjusted x_min to move the graph to the left
y_min, y_max = 42.042274, 42.700273
x_scale = x_max - x_min
y_scale = y_max - y_min

# Load the modified coordinates along with IDs
data = np.loadtxt('modified_coord.csv', delimiter=',', skiprows=1, usecols=(0, 3, 4))

# Convert normalized coordinates to regular coordinates and append them to the data
converted_data = []
for row in data:
    id, norm_lon, norm_lat = row
    norm_lon_flipped = 1 - norm_lon
    norm_lat_flipped = 1 - norm_lat
    lon = norm_lon_flipped * x_scale + x_min
    lat = norm_lat_flipped * y_scale + y_min
    converted_data.append([int(id), lon, lat, norm_lon, norm_lat])

# Save the extended data to a new CSV file
np.savetxt('converted_coordinates.csv', converted_data, delimiter=',', 
           header='ID,Longitude,Latitude,NormalizedLongitude,NormalizedLatitude,', comments='', 
           fmt=['%d', '%f', '%f', '%f', '%f'])