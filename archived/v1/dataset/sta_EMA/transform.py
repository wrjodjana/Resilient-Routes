import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

################# ## check zone in each graph
map_name, max_cap, edge_vmin, edge_vmax, node_size, link_width = 'EMA_new', 8.0, 0.0, 8.0, 15, 3.0


max_cap *= 10
edge_vmax *= 10

G = nx.DiGraph()
ca_list = np.loadtxt('Ca_list.csv'.format(map_name), delimiter=',', skiprows=1)
for edge_ca in ca_list:
    # build graph
    G.add_edge(int(np.round(edge_ca[0])), int(np.round(edge_ca[1])), weight=edge_ca[2]*10)

if 'EMA' in map_name:
    node_list = np.loadtxt('coord.csv'.format(map_name), delimiter=',', encoding='utf-8-sig')

if 'EMA' in map_name:
    x_min, x_max, x_scale = -70.674213, -71.600974, abs(-70.674213 + 71.600974)
    y_min, y_max, y_scale = 42.042274, 42.700273, abs(42.042274 - 42.700273)
    pos = {int(r[0]): (r[3]*x_scale + x_min, r[4]*y_scale+y_min) for r in node_list}




import matplotlib.pylab as pylab
params = {"text.usetex": False,
         'font.size': 20,
         'figure.figsize': [8, 6]}
pylab.rcParams.update(params)
plt.rcParams['figure.dpi'] = 200

fig, ax = plt.subplots()
nx.draw_networkx_nodes(G, pos=pos, node_size=node_size, ax=ax)

cmap = plt.cm.get_cmap('copper')
edge_colors = [G[u][v]['weight'] for u, v in G.edges()]
nx.draw_networkx_edges(G, pos=pos, edge_color=edge_colors, style='-', arrows=False, \
    edge_cmap=cmap, edge_vmin=edge_vmin, edge_vmax=edge_vmax, ax=ax, width=link_width)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = edge_vmin, vmax=edge_vmax))
sm._A = []
cbar = plt.colorbar(sm)
cbar.set_label(r'Link Capacity $(\times 10^2)$')

if map_name == 'ANAHEIM_new':
    ax.set_xticks((-118.00, -117.90, -117.80))
    ax.set_yticks((33.75, 33.79, 33.83, 33.87))
if map_name == 'Sioux_fall_new':
    ax.set_xticks((-96.8, -96.75, -96.7))
    ax.set_yticks((43.49, 43.53, 43.57, 43.61))
if map_name == 'EMA_new':
    ax.set_xticks((-70.4, -70.2, -70.0, -69.8))
    ax.set_yticks((42.1, 42.3, 42.5, 42.7))
ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.tight_layout()

plt.savefig('map.jpg'.format(map_name))
