import igraph as ig
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
def get_community_colormap(g):
    """
    Dynamically generates a color palette mapping for any number of communities.
    """
    # Find all unique community IDs, excluding -1 (which is used for issues)
    communities = list(set([v['community'] for v in g.vs if v['node_type'] == 'actor' and v['community'] != -1]))
    
    # Use a diverse matplotlib colormap (tab20 gives 20 distinct colors)
    cmap = plt.get_cmap('tab20')
    
    color_map = {}
    for i, comm in enumerate(communities):
        color_map[comm] = mcolors.to_hex(cmap(i % 20))
        
    return color_map


def visualize_social_layer(g, filename="social_network.png"):
    """
    Plots ONLY the actors and their social ties.
    Saves the output to the specified filename.
    """
    # 1. Filter the graph to only include actors
    actor_nodes = g.vs.select(node_type='actor')
    social_g = g.subgraph(actor_nodes)
    
    # Ensure we only include social edges (safety check)
    social_edges = social_g.es.select(edge_type='social')
    social_g = social_g.subgraph_edges(social_edges, delete_vertices=False)

    # 2. Assign dynamic colors based on community
    color_map = get_community_colormap(g)
    social_g.vs['color'] = [color_map.get(v['community'], '#CCCCCC') for v in social_g.vs]
    
    # 3. Style the edges
    social_g.es['color'] = 'grey'
    
    # 4. Plot and save
    layout = social_g.layout_fruchterman_reingold()
    
    ig.plot(
        social_g,
        target=filename,
        layout=layout,
        vertex_size=8,
        vertex_frame_width=0.5,
        edge_width=0.3,
        bbox=(800, 800),
        margin=50
    )
    print(f"Social layer saved to {filename}")


def visualize_ideological_layer(g, filename="ideological_network.png"):
    """
    Plots actors and issues, but ONLY shows attitudinal ties.
    Saves the output to the specified filename.
    """
    # 1. Filter the graph to ONLY include attitude edges
    attitude_edges = g.es.select(edge_type='attitude')
    attitude_g = g.subgraph_edges(attitude_edges, delete_vertices=False)
    
    # (Optional) Remove actor nodes that have no opinions at all to declutter the graph
    # isolates = [v.index for v in attitude_g.vs if attitude_g.degree(v) == 0]
    # attitude_g.delete_vertices(isolates)

    # 2. Assign colors to nodes
    color_map = get_community_colormap(g)
    node_colors = []
    node_sizes = []
    
    for v in attitude_g.vs:
        if v['node_type'] == 'issue':
            node_colors.append('yellow')
            node_sizes.append(18)  # Make issues larger so they stand out
        else:
            node_colors.append(color_map.get(v['community'], '#CCCCCC'))
            node_sizes.append(6)   # Make actors smaller
            
    attitude_g.vs['color'] = node_colors
    attitude_g.vs['size'] = node_sizes

    # 3. Assign colors to edges based on opinion value
    edge_colors = []
    for e in attitude_g.es:
        val = e['opinion_val']
        if val == 1:
            edge_colors.append("#28af46df") # Matplotlib standard green
        elif val == -1:
            edge_colors.append("#ca2d2d") # Matplotlib standard red
        else:
            edge_colors.append('grey')
            
    attitude_g.es['color'] = edge_colors

    # 4. Plot and save
    # Fruchterman-Reingold naturally pulls connected actors closer to their issues
    layout = attitude_g.layout_fruchterman_reingold()
    
    ig.plot(
        attitude_g,
        target=filename,
        layout=layout,
        vertex_frame_width=0.5,
        edge_width=0.3,
        bbox=(800, 800),
        margin=50
    )
    print(f"Ideological layer saved to {filename}")


#################
################ PLOTTING
################


def plot_relational_polarization_LFR(df_results):
    """
    Generates a publication-ready line plot for Relational Polarization
    comparing 3 different gamma values using standard error bars.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
    
    # Track the tested gammas (2.0, 2.5, 3.0)
    gamma_values = sorted(df_results['gamma'].unique())
    
    # Publication-ready shades of blue/teal for structural variation
    colors = {2.0: "red", 2.5: "blue", 3.0: "green"}
    markers = {2.0: 'o', 2.5: 's', 3.0: '^'}
    
    for gamma in gamma_values:
        # Filter data for this specific exponent configuration
        df_gamma = df_results[df_results['gamma'] == gamma].sort_values('mu')
        
        x = df_gamma['mu']
        y = df_gamma['relational_polarization_mean']
        y_err = df_gamma['relational_polarization_std']
        
        # Plot with explicit error bars instead of a shaded patch
        # ax.errorbar(x, y, yerr=y_err, color=colors.get(gamma, "#186fac"), 
        #             label=f'γ = {gamma}', linewidth=2.0, 
        #             marker=markers.get(gamma, 'o'), markersize=6,
        #             capsize=4, elinewidth=1.5, markeredgewidth=1.5, zorder=3)

        ax.plot(x, y, color=colors.get(gamma, "#d35400"), label=f'γ = {gamma}', 
            linewidth=2.0, marker=markers.get(gamma, 'o'), markersize=6, zorder=3)
        
    # Styling and formatting
    #ax.set_title("The Impact of Scale-Free Exponent (γ) on Relational Polarization", 
    #             fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Cross-community Mixing Parameter μ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Relational Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    avg_c = round(df_results['avg_communities'].mean(), 1)
    param_text = f"N = {df_results['actors'].iloc[0]}\nAvg. Communities = {avg_c}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=12,
        verticalalignment='bottom', bbox=props, zorder=4)
 
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Scale-Free Hub Exponent', loc='upper right', fontsize=14, frameon=True, edgecolor='gray')
    
    plt.tight_layout()
    output_filename = f"results/relational_polarization_n{df_results['actors'].iloc[0]}_c{df_results['communities'].iloc[0]}.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Relational polarization plot saved to {output_filename}")


def plot_ideological_polarization_LFR(df_results):
    """
    Generates a publication-ready line plot for Ideological Polarization
    comparing 3 different gamma values using standard error bars.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
    
    gamma_values = sorted(df_results['gamma'].unique())
    
    # Publication-ready shades of orange/amber/rust for belief systems
    colors = {2.0: "red", 2.5: "blue", 3.0: "green"}
    markers = {2.0: 'o', 2.5: 's', 3.0: '^'}
    
    for gamma in gamma_values:
        df_gamma = df_results[df_results['gamma'] == gamma].sort_values('mu')
        
        x = df_gamma['mu']
        y = df_gamma['ideological_polarization_mean']
        y_err = df_gamma['ideological_polarization_std']
        
        ax.plot(x, y, color=colors.get(gamma, "#d35400"), label=f'γ = {gamma}', 
            linewidth=2.0, marker=markers.get(gamma, 'o'), markersize=6, zorder=3)
        
        # ax.errorbar(x, y, yerr=y_err, color=colors.get(gamma, "#d35400"), 
        #             label=f'γ = {gamma}', linewidth=2.0, 
        #             marker=markers.get(gamma, 'o'), markersize=6,
        #             capsize=4, elinewidth=1.5, markeredgewidth=1.5, zorder=3)

    #ax.set_title("The Impact of Scale-Free Exponent (γ) on Ideological Polarization", 
    #             fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Cross-community Mixing Parameter μ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Ideological Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    avg_c = round(df_results['avg_communities'].mean(), 1)
    param_text = f"N = {df_results['actors'].iloc[0]}\nAvg. Communities = {avg_c}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='bottom', bbox=props, zorder=4)
    
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0, right=0.8)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Scale-Free Hub Exponent', loc='upper right', fontsize=14, frameon=True, edgecolor='gray')
    
    plt.tight_layout()
    output_filename = f"results/ideological_polarization_n{df_results['actors'].iloc[0]}_c{df_results['communities'].iloc[0]}.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Ideological polarization plot saved to {output_filename}")


def plot_relational_polarization_SBM(df_results):
  
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
        
    communities = sorted(df_results['communities'].unique())
        
    # Publication-ready shades of blue/teal for structural variation
    colors = {2: "red", 4: "blue", 8: "green"}
    markers = {2: 'o', 4: 's', 8: '^'}
        
    for comm_no in communities:
        # Filter data for this specific exponent configuration
        df_gamma = df_results[df_results['communities'] == comm_no].sort_values('ratio')
            
        x = df_gamma['ratio']
        y = df_gamma['relational_polarization_mean']
        y_err = df_gamma['relational_polarization_std']
            
        # Plot with explicit error bars instead of a shaded patch
        # ax.errorbar(x, y, yerr=y_err, color=colors.get(comm_no, "#186fac"), 
        #                 label=f'Communities = {comm_no}', linewidth=2.0, 
        #                 marker=markers.get(comm_no, 'o'), markersize=6,
        #                 capsize=4, elinewidth=1.5, markeredgewidth=1.5, zorder=3)

        ax.plot(x, y, color=colors.get(comm_no, "#186fac"), label=f'Communities = {comm_no}', 
            linewidth=2.0, marker=markers.get(comm_no, 'o'), markersize=6, zorder=3)
     
    ax.set_xlabel("Cross-community tie ratio ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Relational Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
        
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
   
    param_text = f"N = {df_results['actors'].iloc[0]}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='bottom', bbox=props, zorder=4)
    
        
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
        
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Number of communities', loc='upper right', fontsize=14, frameon=True, edgecolor='gray')
        
    plt.tight_layout()
    output_filename = f"results/relational_polarization_n{df_results['actors'].iloc[0]}_sbm.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
        
    print(f"Relational polarization plot saved to {output_filename}")

def plot_ideological_polarization_SBM(df_results):
  
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
        
    communities = sorted(df_results['communities'].unique())
        
        # Publication-ready shades of blue/teal for structural variation
    colors = {2: "red", 4: "blue", 8: "green"}
    markers = {2: 'o', 4: 's', 8: '^'}
        
    for comm_no in communities:
            # Filter data for this specific exponent configuration
        df_gamma = df_results[df_results['communities'] == comm_no].sort_values('ratio')
            
        x = df_gamma['ratio']
        y = df_gamma['ideological_polarization_mean']
        y_err = df_gamma['ideological_polarization_std']
            
            # Plot with explicit error bars instead of a shaded patch
        # ax.errorbar(x, y, yerr=y_err, color=colors.get(comm_no, "#186fac"), 
        #                 label=f'Communities = {comm_no}', linewidth=2.0, 
        #                 marker=markers.get(comm_no, 'o'), markersize=6,
        #                capsize=4, elinewidth=1.5, markeredgewidth=1.5, zorder=3)

        ax.plot(x, y, color=colors.get(comm_no, "#186fac"), label=f'Communities = {comm_no}', 
            linewidth=2.0, marker=markers.get(comm_no, 'o'), markersize=6, zorder=3)
 
    ax.set_xlabel("Cross-community tie ratio ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Ideological Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
        
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    
    param_text = f"N = {df_results['actors'].iloc[0]}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='bottom', bbox=props, zorder=4)
        
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
        
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Number of communities', loc='upper right', fontsize=14, frameon=True, edgecolor='gray')
        
    plt.tight_layout()
    output_filename = f"results/ideological_polarization_n{df_results['actors'].iloc[0]}_sbm.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
        
    print(f"Ideological polarization plot saved to {output_filename}")
