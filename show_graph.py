# from os import name

# import matplotlib
# import numpy as np
# from igraph import Graph
# from data_generation import add_initial_opinions, generate_base_network_SBM
# from measure_polarization import measure_network_polarization
# from utils import get_cross_density
# from visualization import show_graph

# import pandas as pd
# if __name__ == "__main__":
   
#     num_actors = 150
#     num_issues = 4
#     num_communities = 3
#     p_in = 0.5
#     p_out = 0.01

#     g = generate_base_network_SBM(
#         nodes=num_actors, 
#         communities=num_communities, 
#         p_in=p_in, 
#         p_out=p_out,
#         seed=42
#     )
    
#     g = add_initial_opinions(g, 
#                             num_actors, 
#                             num_communities,
#                             num_issues, 
#                             seed=42, 
#                             p_agree=0.5,
#                             seeds_per_community=5)
    
#     show_graph(g, filename=None, nodes=num_actors, issues=num_issues, communities=num_communities)

import networkx as nx
import matplotlib.pyplot as plt

# Show toy networ for paper
G = nx.Graph()


actors_comm1 = ['A', 'B']
actors_comm2 = ['C', 'D']
issues = ['1', '2']

G.add_nodes_from(actors_comm1 + actors_comm2 + issues)


social_edges = [
    ('A', 'B'),  # Community 1 internal tie
    ('C', 'D'),  # Community 2 internal tie
    ('B', 'C')   # Single cross-community tie
]
G.add_edges_from(social_edges, edge_type='social')


attitude_edges = [
    ('A', '1', 'green'), ('B', '1', 'green'),
    ('A', '2', 'red'),   ('B', '2', 'red'),
    ('C', '1', 'red'),   ('D', '1', 'red'),
    ('C', '2', 'green'), ('D', '2', 'green')
]
for u, v, color in attitude_edges:
    G.add_edge(u, v, edge_type='attitude', color=color)


pos = {
    'A': (-0.2,  0.4), 'B': (-0.2, -0.4),  # Comm 1 clustered on the left
    'C': ( 0.2,  0.4), 'D': ( 0.2, -0.4),  # Comm 2 clustered on the right
    '1': (0,  1.25),                  # Above both communities
    '2': (0, -1.25)                   # Below both communities
}


plt.figure(figsize=(7, 7))

# Draw actor nodes (colored by community)
nx.draw_networkx_nodes(G, pos, nodelist=actors_comm1, node_color='lightblue', node_size=3000, edgecolors='black')
nx.draw_networkx_nodes(G, pos, nodelist=actors_comm2, node_color="#f69e63", node_size=3000, edgecolors='black')

# Draw issue nodes (yellow squares)
nx.draw_networkx_nodes(G, pos, nodelist=issues, node_shape='s', node_color='yellow', node_size=3000, edgecolors='black')

# Draw thick black lines for social edges
nx.draw_networkx_edges(G, pos, edgelist=social_edges, width=3, edge_color='black')

# Draw dashed colored lines for attitude edges
green_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('color') == 'green']
red_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('color') == 'red']
nx.draw_networkx_edges(G, pos, edgelist=green_edges, width=2, edge_color='green', style='-')
nx.draw_networkx_edges(G, pos, edgelist=red_edges, width=2, edge_color='red', style='-')

# Draw Labels
nx.draw_networkx_labels(G, pos, font_size=25, font_weight='light')

plt.title("Polarized Toy Network", fontsize=25, fontweight='light', pad=20)
plt.axis('off')
plt.tight_layout()
plt.savefig("polarized_toy_network.png", dpi=300)