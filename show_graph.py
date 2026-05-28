from os import name

import matplotlib
import numpy as np
from igraph import Graph
from data_generation import add_initial_opinions, add_issues_and_opinions, generate_base_network_SBM
from measure_polarization import measure_network_polarization
from utils import get_cross_density
from visualization import show_graph

import pandas as pd
if __name__ == "__main__":
   
    num_actors = 150
    num_issues = 4
    num_communities = 3
    p_in = 0.5
    p_out = 0.01

    g = generate_base_network_SBM(
        nodes=num_actors, 
        communities=num_communities, 
        p_in=p_in, 
        p_out=p_out,
        seed=42
    )
    
    g = add_initial_opinions(g, 
                            num_actors, 
                            num_communities,
                            num_issues, 
                            seed=42, 
                            p_agree=0.5,
                            seeds_per_community=5)
    
    show_graph(g, filename=None, nodes=num_actors, issues=num_issues, communities=num_communities)