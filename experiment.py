import random
import numpy as np
from igraph import Graph
from data_generation import add_initial_opinions, add_issues_and_opinions, generate_base_network_LFR, generate_base_network_SBM
from measure_polarization import measure_network_polarization
from simulate_evolution import simulate_network_evolution
from utils import get_cross_density
from visualization import show_graph, plot_experiment_results
import matplotlib.pyplot as plt
import pandas as pd


def run_experiment_SBM(num_actors, num_issues, num_communities, p_in, p_out_values, seed=42, iterations=10):

    results = []
    for p_out in p_out_values:
        
        iteration_results = [] 
        
        for i in range(iterations):
            
            g = generate_base_network_SBM(
                 nodes=num_actors, 
                 communities=num_communities,  
                 p_in=p_in, 
                 p_out=p_out,
                 seed=seed
            )

            g = add_initial_opinions(g,
                                     nodes=num_actors,
                                     communities=num_communities,
                                     issues=num_issues,
                                     seed=seed,
                                     p_agree=0.5,
                                     seeds_per_community=5)


            g = simulate_network_evolution(g, nodes=num_actors, issues=num_issues, threshold=0.1, steps=30)
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
    plot_experiment_results(df_final_summary)

def run_experiment_LFR(num_actors, num_issues, gamma, beta, min_degree, max_degree, mu_values, seed=42, iterations=10):

    results = []
    for mu in mu_values:
        iteration_results = [] 
        min_community =np.ceil(max_degree * (1 - mu))
        max_community = np.floor(num_actors / 5)
        for i in range(iterations):
            
            g, community_count = generate_base_network_LFR(
                nodes=num_actors, 
                gamma=gamma,
                beta=beta,
                mu=mu,
                min_degree=min_degree,
                max_degree=max_degree,
                min_community=min_community,
                max_community=max_community,
                seed=seed
            )

            g = add_initial_opinions(g,
                                     nodes=num_actors,
                                     communities=community_count,
                                     issues=num_issues,
                                     seed=seed,
                                     p_agree=0.5,
                                     seeds_per_community=5)


            g = simulate_network_evolution(g, nodes=num_actors, issues=num_issues, threshold=0.1, steps=30)
            metrics = measure_network_polarization(g)
            density = get_cross_density(g)
            if (density != mu):
                print(f"{density} does not match expected mu: {mu}")
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
    plot_experiment_results(df_final_summary)


if __name__ == "__main__":
    
    # Define parameters
    num_actors = 160
    num_issues = 10
    num_communities = 2
    p_in = 0.15
    iterations = 10
    #results = []
    seed = 42
    # Test Loop
    p_out_values = np.linspace(0.01, p_in, 12)
    
    mu_values = np.linspace(0.05, 0.6, 12)
    gamma = 2.5 # standard choice for LFR
    beta = 1.5 # standard choice for LFR
    min_degree = np.ceil(np.log(num_actors)) # standard choice for LFR
    max_degree = np.floor(np.sqrt(num_actors)) # standard choice for LFR
    run_experiment_SBM(num_actors, num_issues, num_communities, p_in, p_out_values, seed, iterations)
    #run_experiment_LFR(num_actors, num_issues, gamma, beta, min_degree, max_degree, mu_values, seed, iterations)