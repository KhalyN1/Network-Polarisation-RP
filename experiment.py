import random
import numpy as np
from igraph import Graph
from data_generation import add_initial_opinions, add_initial_opinions_new, generate_base_network_LFR, generate_base_network_SBM
from measure_polarization import measure_network_polarization
from simulate_evolution import simulate_network_evolution, simulate_network_evolution_new
from utils import get_cross_density
from visualization import visualize_ideological_layer, visualize_social_layer
import matplotlib.pyplot as plt
import pandas as pd


def run_experiment_SBM(num_actors, num_issues, num_communities, p_in, p_out_values, iterations=10):

    seed = 42
    results = []
    for p_out_idx, p_out in enumerate(p_out_values):
        
        iteration_results = [] 
        
        for i in range(iterations):
            
            current_seed = seed + i + p_out_idx * iterations
            random.seed(current_seed)
            np.random.seed(current_seed)

            g = generate_base_network_SBM(
                 nodes=num_actors, 
                 communities=num_communities,  
                 p_in=p_in, 
                 p_out=p_out,
                 seed=current_seed
            )

            g = add_initial_opinions_new(g,
                                     nodes=num_actors,
                                     communities=num_communities,
                                     issues=num_issues,
                                     seed=current_seed,
                                     p_agree=0.2,
                                     seeds_per_community_ratio=0.2)

            
            g = simulate_network_evolution(g, nodes=num_actors, issues=num_issues, steps=30)
            metrics = measure_network_polarization(g)
            density = get_cross_density(g)
            
            iteration_results.append({
                'density': density,
                'relational_polarization': metrics['relational_polarization'],
                'ideological_polarization': metrics['ideological_polarization']
            })
        df_step = pd.DataFrame(iteration_results)
        results.append({
            'density_mean': df_step['density'].mean(),
            'density_std': df_step['density'].std(),
            'relational_polarization_mean': df_step['relational_polarization'].mean(),
            'relational_polarization_std': df_step['relational_polarization'].std(),
            'ideological_polarization_mean': df_step['ideological_polarization'].mean(),
            'ideological_polarization_std': df_step['ideological_polarization'].std(),
            'communities': num_communities,
            'actors': num_actors,
            'issues': num_issues,
        })    
            
    df_final_summary = pd.DataFrame(results)
    #plot_experiment_results(df_final_summary)

def run_experiment_LFR(num_actors, num_issues, gamma, beta, min_degree, max_degree, mu_values, iterations=10):

    seed = 42

    results = []
    for mu_idx, mu in enumerate(mu_values):
        iteration_results = [] 
        min_community_treshold = int(np.ceil(max_degree * (1 - mu))) + 1
        min_community = max(min_degree, min_community_treshold)
        max_community = num_actors // 3
        for i in range(iterations):
            
            current_seed = seed + i + mu_idx * iterations
            random.seed(current_seed)
            np.random.seed(current_seed)

            g, community_count = generate_base_network_LFR(
                nodes=num_actors, 
                gamma=gamma,
                beta=beta,
                mu=mu,
                min_degree=min_degree,
                max_degree=max_degree,
                min_community=min_community,
                max_community=max_community,
                seed=current_seed
            )

            g = add_initial_opinions_new(g,
                                     nodes=num_actors,
                                     issues=num_issues,
                                     communities=community_count,
                                     p_agree=0.2,
                                     seeds_per_community_ratio=0.2,
                                     seed=current_seed)
            
            
            g = simulate_network_evolution(g, nodes=num_actors, issues=num_issues, steps=30)
            metrics = measure_network_polarization(g)
            density = get_cross_density(g)
        
            iteration_results.append({
                'density': density,
                'relational_polarization': metrics['relational_polarization'],
                'ideological_polarization': metrics['ideological_polarization']
            })
        df_step = pd.DataFrame(iteration_results)
        results.append({
            'density_mean': df_step['density'].mean(),
            'density_std': df_step['density'].std(),
            'relational_polarization_mean': df_step['relational_polarization'].mean(),
            'relational_polarization_std': df_step['relational_polarization'].std(),
            'ideological_polarization_mean': df_step['ideological_polarization'].mean(),
            'ideological_polarization_std': df_step['ideological_polarization'].std(),
            'communities': community_count,
            'actors': num_actors,
            'issues': num_issues,
        })
    df_final_summary = pd.DataFrame(results)
    #plot_experiment_results(df_final_summary)
    

if __name__ == "__main__":
    
    # Define parameters
    N = 500
    num_issues = 10
    num_communities = 4
    c_in = 20
    p_in = c_in / N * num_communities
    iterations = 20
    #results = []
    # seed = 42
    # random.seed(seed)
    # np.random.seed(seed)
    # Test Loop
    p_out_values = np.linspace(0.01, 0.7 * p_in, 12)
    
    mu_values = np.linspace(0.1, 0.6, 12)
    gamma = 2.0 # node exponent
    beta = 1.5 # community size distribution
    min_degree = np.ceil(np.log(N)) 
    max_degree = np.floor(np.sqrt(N)) 
    run_experiment_SBM(N, num_issues, num_communities, p_in, p_out_values, iterations)
    #run_experiment_LFR(N, num_issues, gamma, beta, min_degree, max_degree, mu_values, iterations)