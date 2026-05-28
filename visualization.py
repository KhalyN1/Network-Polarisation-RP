import igraph as ig
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

def show_graph(g, filename=None, nodes=250, issues=10, communities=None):
    # 1. DYNAMICALLY DETECT COMMUNITIES FROM THE GRAPH DATA
    # This prevents parameter mismatches from breaking the layout
    all_communities = sorted(list(set(v["community"] for v in g.vs if v["node_type"] == "actor" and v["community"] is not None)))
    actual_community_count = len(all_communities)
    
    print(f"DEBUG: Graph actually contains {actual_community_count} unique communities: {all_communities}")

    # 2. Build Gradient Color Palette based on ACTUAL community count
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", ["skyblue", "orange"])
    color_dict = {-1: "yellow"}
    
    if actual_community_count == 1:
        color_dict[all_communities[0]] = "skyblue"
    elif actual_community_count > 1:
        for idx, comm_id in enumerate(all_communities):
            rgba = cmap(idx / (actual_community_count - 1)) 
            color_dict[comm_id] = mcolors.to_hex(rgba)

    # Assign colors dynamically using .get() fallbacks
    g.vs["color"] = [color_dict.get(v["community"], "#a0a0a0") if v["node_type"] == "actor" else "yellow" for v in g.vs]

    # Node Styling
    shape_dict = {'actor': 'circle', 'issue': 'rectangle'}
    g.vs["shape"] = [shape_dict.get(ntype, 'circle') for ntype in g.vs["node_type"]]

    size_dict = {'actor': 25, 'issue': 60}
    g.vs["size"] = [size_dict.get(ntype, 30) for ntype in g.vs["node_type"]]

    # Edge Colors
    edge_colors = []
    for edge in g.es:
        if edge["edge_type"] == "social":
            edge_colors.append("#e8e8e8") # Very light gray so 250 nodes don't look muddy
        elif edge["edge_type"] == "attitude": 
            edge_colors.append("#68da4e" if edge["opinion_val"] == 1 else "#c73e3e") 
    g.es["color"] = edge_colors

    # 3. COORDINATE CALCULATION
    coords = [None] * len(g.vs)
    midpoint_x = 50.0  
    
    # Position Actor Clusters symmetrically along X-axis
    community_centers = {}
    if actual_community_count > 1:
        community_span = 70.0 # Widen layout field so 5 groups don't blend together
        start_x = midpoint_x - (community_span / 2.0)
        step_x = community_span / (actual_community_count - 1)
        for idx, comm_id in enumerate(all_communities):
            community_centers[comm_id] = start_x + (idx * step_x)
    else:
        community_centers[all_communities[0]] = midpoint_x

    for v in g.vs:
        if v["node_type"] == "actor":
            comm = v["community"]
            center_x = community_centers.get(comm, midpoint_x)
            # Give 250 nodes room to jitter without overlapping other clusters
            x_pos = center_x + random.uniform(-3.5, 3.5)  
            y_pos = random.uniform(2.1, 2.9)         
            coords[v.index] = (x_pos, y_pos)

    # Position Issue Nodes symmetrically along X-axis
    issue_nodes = [v for v in g.vs if v["node_type"] == "issue"]
    num_issues = len(issue_nodes)
    
    if num_issues > 1:
        issue_span = 85.0 
        start_issue_x = midpoint_x - (issue_span / 2.0)
        step_issue_x = issue_span / (num_issues - 1)
        
        for idx, v in enumerate(issue_nodes):
            x_pos = start_issue_x + (idx * step_issue_x)
            y_pos = 4.3 if idx % 2 == 0 else 0.7 # Alternating top/bottom horizons
            coords[v.index] = (x_pos, y_pos)
    elif num_issues == 1:
        coords[issue_nodes[0].index] = (midpoint_x, 4.3)

    # Fix any unassigned node positions to center safezone
    for i in range(len(coords)):
        if coords[i] == None:
            coords[i] = (midpoint_x, 2.5)

    # 4. RENDERING BOUNDARIES
    layout = ig.Layout(coords)
    fig, ax = plt.subplots(figsize=(16, 12)) 

    ig.plot(
        g,
        target=ax,
        layout=layout,
        vertex_label_size=7,
        vertex_label_dist=1.1,
        edge_arrow_size=4,
        edge_width=0.6, 
        directed=True
    )

    ax.set_title(f"Multilevel Polarization Network ({actual_community_count} Communities Shown)", fontsize=16)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 5)
    plt.axis('off')
    
    display_comm = communities if communities else actual_community_count
    output_filename = filename if filename else f"graph_visuals/graph_n{nodes}_i{issues}_c{display_comm}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_experiment_results(df_results):
    """Generates and saves a publication-ready line plot of the sweep."""
    plt.figure(figsize=(8, 8))
    
    
    plt.plot(
        df_results['density_mean'], df_results['relational_polarization_mean'], #yerr=df_results['relational_polarization_std'], 
        color="#186fac", label='Relational Polarization', 
        linewidth=3, markersize=0.5, alpha=1
    )
                 
    plt.plot(
        df_results['density_mean'], df_results['ideological_polarization_mean'], #yerr=df_results['ideological_polarization_std'], 
        color='orange', label='Ideological Polarization', 
        linewidth=3, markersize=0.5, alpha=1
    )

    plt.plot([], [], ' ', label=f'communities = {df_results["communities"].iloc[0]}')
    plt.plot([], [], ' ', label=f'n = {df_results["actors"].iloc[0]}')
    plt.title("The Impact of Cross-Community Social Structure on Polarization", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Cross-Community Social Tie Density", fontsize=10, labelpad=10)
    plt.ylabel("Polarization Score", fontsize=10, labelpad=10)
    
    plt.ylim(0, 1.05)
    plt.xlim(left=0)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper right', fontsize=11, frameon=True, shadow=False)
    # Save the output figure
    output_filename = f"results/polarization_n{df_results['actors'].iloc[0]}_c{df_results['communities'].iloc[0]}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print("Done")
