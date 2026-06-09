from os import name

import matplotlib
import numpy as np
from igraph import Graph
from data_generation import add_initial_opinions, generate_base_network_SBM, generate_base_network_LFR
from visualization import visualize_combined_network
from simulate_evolution import simulate_network_evolution

import pandas as pd
if __name__ == "__main__":
   
    N = 500
    gamma = 2.5
    beta = 1.5
    num_issues = 5
    num_communities = 3
    p_in = 0.5
    p_out = 0.01
    mu = 0.1
    min_degree = 5
    max_degree = min(50, N//5)
    min_community = int(max_degree * 1.2)
    max_community = N // 4
    g, num_communities = generate_base_network_LFR(N, gamma, beta, mu, min_degree, 
                                                   max_degree, min_community, 
                                                   max_community, seed=44)
    
    g = add_initial_opinions(g, 
                            N, 
                            num_issues, 
                            num_communities,
                            seed=42, 
                            p_agree=0.2,
                            seeds_per_community_ratio=0.1)
    
    #visualize_combined_network(g, filename="graph_visuals/initial_n500_mu04.png")

    g, total_steps = simulate_network_evolution(g, N, num_issues, 30, 0.05)
    #visualize_combined_network(g, filename="graph_visuals/final_n500_mu04.png")
    

