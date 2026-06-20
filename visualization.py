import igraph as ig
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import random
def get_community_colormap(g):
    """
    Dynamically generates a color palette mapping for any number of communities.
    """
    # Find all unique community IDs, excluding -1 (which is used for issues)
    communities = list(set([v['community'] for v in g.vs if v['node_type'] == 'actor' and v['community'] != -1]))
    
   
    cmap = plt.get_cmap('tab20')
    
    color_map = {}
    for i, comm in enumerate(communities):
        color_map[comm] = mcolors.to_hex(cmap(i % 20))
        
    return color_map

def visualize_combined_network(g, filename="combined_network.png"):
    """
    Plots a multi-layer graph with issues in the center and communities 
    clustered in a ring around them.
    """
    color_map = get_community_colormap(g)
    
    layout = []
    
    # Identify nodes
    issues = g.vs.select(node_type='issue')
    communities = list(set([v['community'] for v in g.vs if v['node_type'] == 'actor' and v['community'] != -1]))
    
    # Geometry parameters
    R_OUTER = 20.0  # Radius of the community ring
    R_INNER = 2.0   # Spread of the issue nodes in the center
    CLUSTER_SPREAD = 3.5 # How loosely packed the actors are in their community cluster
    
    # Pre-calculate center coordinates for each community in a circle
    num_comms = len(communities)
    comm_centers = {}
    for i, comm in enumerate(communities):
        
        angle = i * (2 * np.pi / num_comms)
        comm_centers[comm] = (R_OUTER * np.cos(angle), R_OUTER * np.sin(angle))
    
    # Assign coordinates to each node
    k = 0 
    nodes = g.vcount()
    
    for v in g.vs:
        if v['node_type'] == 'issue':
            # Place issues in the center (slightly staggered if there are multiple)
            angle = k * (2 * np.pi / len(issues))
            ix = R_INNER * np.cos(angle)
            iy = R_INNER * np.sin(angle)
            layout.append((ix, iy))
            k += 1
        else:
            # Place actors around their community's designated center coordinate
            cx, cy = comm_centers.get(v['community'], (0,0))
            # Use normal distribution to create a natural looking cluster\
            #angle = random.uniform(0, 2 * np.pi)
            #min_dist = 0.20 * CLUSTER_SPREAD
            #max_dist = 1 * CLUSTER_SPREAD
       
            ax = random.gauss(cx, CLUSTER_SPREAD)
            ay = random.gauss(cy, CLUSTER_SPREAD)
            layout.append((ax, ay))

    node_colors, node_shapes, node_sizes = [], [], []
    
    for v in g.vs:
        if v['node_type'] == 'issue':
            node_colors.append('yellow')
            node_shapes.append('square') # Stars or large squares for issues
            node_sizes.append(25)
        else:
            comm = v['community']
            node_colors.append(color_map.get(comm, '#CCCCCC'))
            node_shapes.append('circle')
            node_sizes.append(15)
            
    g.vs['color'] = node_colors
    g.vs['shape'] = node_shapes
    g.vs['size'] = node_sizes
    
    edge_colors, edge_widths = [], []
    
    for e in g.es:
        if e['edge_type'] == 'social':
            # Check if it's an internal or cross-community tie
            source_comm = g.vs[e.source]['community']
            target_comm = g.vs[e.target]['community']
            
            if source_comm == target_comm:
                # Internal ties: slightly darker/thicker to show dense clusters
                edge_colors.append('rgba(150, 150, 150, 0.8)')
                edge_widths.append(0.8)
            else:
                # Cross-community ties: lighter, matching the dashed look in your image
                edge_colors.append('rgba(200, 200, 200, 0.8)')
                edge_widths.append(0.8)
                
        elif e['edge_type'] == 'attitude':
            val = e['opinion_val']
            # Make attitudinal edges semi-transparent so they don't overpower the social structure
            if val == 1:
                edge_colors.append('rgba(40, 175, 70, 0.7)')  # Transparent Green
            elif val == -1:
                edge_colors.append('rgba(202, 45, 45, 0.7)')  # Transparent Red
            else:
                edge_colors.append('rgba(0, 0, 0, 0.1)')
            edge_widths.append(0.8)
            
    g.es['color'] = edge_colors
    g.es['width'] = edge_widths

   
    ig.plot(
        g,
        target=filename,
        layout=layout, 
        vertex_frame_width=0.5,
        vertex_frame_color='black',
        bbox=(1200, 1200),
        margin=80,
        background='white'
    )
    print(f"Combined layered network saved to {filename}")
#################
################ PLOTTING
################


def plot_relational_polarization_LFR(df_results, output_filename=None):
    """
    Generates a publication-ready line plot for Relational Polarization
    comparing 3 different N values using standard error bars.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
    

    N_values = sorted(df_results['actors'].unique())
    
    
    colors = {500: "#be0006", 1000: "#0000a2", 5000: "#01c469"}
    markers = {500: 'o', 1000: 's', 5000: '^'}
    
    for N in N_values:
    
        df_N = df_results[df_results['actors'] == N].sort_values('mu')
        
        x = df_N['mu']
        y = df_N['relational_polarization_mean']
        y_err = df_N['relational_polarization_std']
        gamma = df_N['gamma'].unique()[0]
        beta = df_N['beta'].unique()[0]
       
        ax.plot(x, y, color=colors.get(N, "#d35400"), label=f'N = {N}', 
           linewidth=2.0, marker=markers.get(N, 'o'), markersize=6, zorder=3)
        
        ax.fill_between(x, y - y_err, y + y_err,
                color=colors.get(N, "#d35400"),
                alpha=0.15, zorder=2)
        
    # Styling and formatting
    #ax.set_title("The Impact of Scale-Free Exponent (γ) on Relational Polarization", 
    #             fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Cross-community Mixing Parameter μ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Relational Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    #avg_c = round(df_results['avg_communities'].mean(), 1)
    param_text = f"γ = {gamma}\n β = {beta}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=15,
        verticalalignment='bottom', bbox=props, zorder=4)
 
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Network size', loc='upper right', fontsize=17, frameon=True, edgecolor='gray')
    
    plt.tight_layout()
    if output_filename is None:
        output_filename = f"results/relational_polarization_lfr.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Relational polarization plot saved to {output_filename}")


def plot_ideological_polarization_LFR(df_results, output_filename=None):
    """
    Generates a publication-ready line plot for Ideological Polarization
    comparing 3 different N values using standard error bars.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
    
    N_values = sorted(df_results['actors'].unique())
    
    colors = {500: "#be0006", 1000: "#0000a2", 5000: "#01c469"}
    markers = {500: 'o', 1000: 's', 5000: '^'}
    
    for N in N_values:
        df_N = df_results[df_results['actors'] == N].sort_values('mu')
        
        x = df_N['mu']
        y = df_N['ideological_polarization_mean']
        y_err = df_N['ideological_polarization_std']
        gamma = df_N['gamma'].unique()[0]
        beta = df_N['beta'].unique()[0]
        ax.plot(x, y, color=colors.get(N, "#d35400"), label=f'N = {N}', 
            linewidth=2.0, marker=markers.get(N, 'o'), markersize=6, zorder=3)
        
        ax.fill_between(x, y - y_err, y + y_err,
                color=colors.get(N, "#d35400"),
                alpha=0.15, zorder=2)
    
    ax.set_xlabel("Cross-community Mixing Parameter μ", fontsize=16, fontweight='bold', labelpad=10)
    ax.set_ylabel("Ideological Polarization Score", fontsize=16, fontweight='bold', labelpad=10)
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
    #avg_c = round(df_results['avg_communities'].mean(), 1)
    param_text = f"γ = {gamma}\n β = {beta}"
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=15,
            verticalalignment='bottom', bbox=props, zorder=4)
    
    ax.set_ylim(0, 1.05)
    ax.set_xlim(left=0, right=0.8)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Network size', loc='upper right', fontsize=17, frameon=True, edgecolor='gray')
    
    plt.tight_layout()
    if output_filename is None:
        output_filename = f"results/ideological_polarization_lfr.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
    
    print(f"Ideological polarization plot saved to {output_filename}")


def plot_relational_polarization_SBM(df_results, output_filename=None):
  
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
        
    communities = sorted(df_results['communities'].unique())
        
    colors = {2: "#be0006", 4: "#0000a2", 8: "#01c469"}
    markers = {2: 'o', 4: 's', 8: '^'}
        
    for comm_no in communities:
        
        df_comm = df_results[df_results['communities'] == comm_no].sort_values('ratio')
            
        x = df_comm['ratio']
        y = df_comm['relational_polarization_mean']
        y_err = df_comm['relational_polarization_std']
            
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
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=15,
            verticalalignment='bottom', bbox=props, zorder=4)
    
        
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
        
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Number of communities', loc='upper right', fontsize=17, frameon=True, edgecolor='gray')
        
    plt.tight_layout()
    if output_filename is None:
        output_filename = f"results/relational_polarization_n{df_results['actors'].iloc[0]}_sbm.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
        
    print(f"Relational polarization plot saved to {output_filename}")

def plot_ideological_polarization_SBM(df_results, output_filename=None):
  
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(9, 6))
        
    communities = sorted(df_results['communities'].unique())
        
    colors = {2: "#be0006", 4: "#0000a2", 8: "#01c469"}
    markers = {2: 'o', 4: 's', 8: '^'}
        
    for comm_no in communities:
    
        df_comm = df_results[df_results['communities'] == comm_no].sort_values('ratio')
            
        x = df_comm['ratio']
        y = df_comm['ideological_polarization_mean']
        y_err = df_comm['ideological_polarization_std']
            
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
    ax.text(0.03, 0.05, param_text, transform=ax.transAxes, fontsize=15,
            verticalalignment='bottom', bbox=props, zorder=4)
        
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(left=0.0, right=0.8)
        
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(title='Number of communities', loc='upper right', fontsize=17, frameon=True, edgecolor='gray')
        
    plt.tight_layout()
    if output_filename is None:
        output_filename = f"results/ideological_polarization_n{df_results['actors'].iloc[0]}_sbm.png"
    plt.savefig(output_filename, dpi=300)
    plt.close()
        
    print(f"Ideological polarization plot saved to {output_filename}")
