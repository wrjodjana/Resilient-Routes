import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from mpl_toolkits.basemap import Basemap as Basemap



SpreadSheet = np.genfromtxt('map.csv', delimiter=',', dtype=None, encoding='utf-8-sig')
colNames = SpreadSheet[0, :]
node_file = SpreadSheet[1:, :]
id_list = node_file[:, np.where(colNames == 'id')[0][0]].astype(np.int32)
lat_list = node_file[:, np.where(colNames == 'lat')[0][0]].astype(np.float32)
lon_list = node_file[:, np.where(colNames == 'lon')[0][0]].astype(np.float32)
print(node_file)


G = nx.Graph()
for nid, lat, lon in zip(id_list, lat_list, lon_list):
    G.add_node(nid, pos=(lon, lat))

bridge_list = [(0, 1), (0, 5), (1, 2), (1, 5), (2, 3), (3, 4), (3, 7), \
            (4, 8), (5, 9), (6, 10), (6, 12), (7, 8), (7, 10), (7, 15), (8, 16), \
            (9, 18), (10, 11), (10, 13), (11, 14), (11, 15), (12, 13), (12, 19), \
            (14, 15), (14, 21), (14, 22), (15, 17), (16, 17), (16, 23), (17, 22), \
            (18, 19), (18, 26), (19, 20), (20, 24), (20, 29), (21, 22), (21, 24), \
            (22, 25), (23, 25), (24, 25), (24, 27), (25, 28), (26, 33), (27, 29), \
            (28, 30), (28, 31), (30, 31), (31, 32), (31, 35), (32, 36), (33, 34), \
            (34, 35), (35, 36)]
road_list = [(1,6), (2,6), (9,12), (13,20), (13,21), (17,23), (16, 32), \
        (19,26), (23,32), (29,33), (30,34), (33,37), (36,38)]
edge_list = bridge_list + road_list
G.add_edges_from(edge_list)


BBox = (-122.0993, -121.7000, 37.2000, 37.4509)
# extent = -122.0993, -121.7000, 37.2000, 37.4509
fig, ax = plt.subplots()

img = matplotlib.image.imread('map.png')
ax.imshow(img, extent=[-122.0993, -121.7000, 37.2000, 37.4509])
# ax.set_xlim(BBox[0],BBox[1])
# ax.set_ylim(BBox[2],BBox[3])

pos = nx.get_node_attributes(G,'pos')
nx.draw(G, pos, cmap=plt.cm.Blues, node_size=200, with_labels=False, width=2)

ax.axis('off')
ax.axis('equal')
plt.tight_layout()
# plt.subplots_adjust(top=1.0, bottom=0.0, right=1.0, left=0.0, hspace=0, wspace=0)

plt.savefig('res.jpg')

# 
# ax.scatter(df.longitude, df.latitude, zorder=1, alpha= 0.2, c='b', s=10)
# ax.set_title('Plotting Spatial Data on Riyadh Map')
# ax.set_xlim(BBox[0],BBox[1])
# ax.set_ylim(BBox[2],BBox[3])
# # ax.imshow(ruh_m, zorder=0, extent = BBox, aspect= 'equal')

# 