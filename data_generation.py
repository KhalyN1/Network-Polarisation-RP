import igraph as ig
from igraph import Graph
import random
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import opinion_split_2_communities, opinion_split_3_communities
import numpy as np
import igraph as ig
from igraph import Graph
import random
import networkx as nx

def generate_base_network_LFR(nodes:int, gamma:float, beta:float, mu:float, 
                              min_degree:int, max_degree:int, min_community:int=None, max_community:int=None, seed=None):
    '''
    Generates a base network using the LFR benchmark model. NetworkX was used initially as igraph does not have LFR built in.
    '''

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    g = nx.generators.community.LFR_benchmark_graph(
        n=nodes,
        tau1=gamma,
        tau2=beta,
        mu=mu,
        min_degree=min_degree,
        max_degree=max_degree,
        min_community=min_community, 
        max_community=max_community,
        tol=1e-2,
        seed=seed)
    
    community_IDs = {}

    for node in g.nodes():
        comm = frozenset(g.nodes[node]['community'])
        if comm not in community_IDs:
            community_IDs[comm] = len(community_IDs)

    edges = list(g.edges())
    ig_g = Graph(n=nodes, edges=edges, directed=True)

    ig_g.vs['node_type'] = 'actor'
    communities_list = []
    for i in range(nodes):
        comm = frozenset(g.nodes[i]['community'])
        communities_list.append(int(community_IDs[comm]))
    
    ig_g.vs['community'] = communities_list
    
    
    ig_g.es['edge_type'] = 'social'
    ig_g.es['opinion_val'] = None
    
    return ig_g, len(community_IDs)

def generate_base_network_SBM(nodes:int=50, communities:int=2, p_in:float=0.15, p_out:float=0.05, seed=None):
  
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        
    # SBM needs block sizes (sizes of communities)
    base_size = nodes // communities
    block_sizes = [base_size] * communities
    block_sizes[-1] += (nodes - sum(block_sizes)) 
    
    #Also needs pref matrix, with probs of connecting in or out of community.
    pref_matrix = []
    for i in range(communities):
        row = []
        for j in range(communities):
            if i == j:
                row.append(float(p_in))  
            else:
                row.append(float(p_out))  
        pref_matrix.append(row)
        
   # print(ig.__version__)
   # help(ig.Graph.SBM)
   #base graph, before adding issues to it
    g = ig.Graph.SBM(
        pref_matrix=pref_matrix,
        block_sizes=block_sizes,
        directed=True,
    )
   
    g.vs['node_type'] = 'actor'
    communities_list = []
    for i, size in enumerate(block_sizes):
        communities_list.extend([i] * size)
    g.vs['community'] = communities_list
    
    
    g.es['edge_type'] = 'social'
    g.es['opinion_val'] = None

    return g


def assign_initial_platforms(issues:int, p_agree:float, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    platforms = {}
    
    platforms[0] = {issue_idx: random.choice([1, -1]) for issue_idx in range(issues)}
    
    
    platforms[1] = {}
    for issue_idx in range(issues):
        if random.random() < p_agree:
            platforms[1][issue_idx] = platforms[0][issue_idx]  # They agree on this issue
        else:
            platforms[1][issue_idx] = -platforms[0][issue_idx] # They disagree on this issue
            
    return platforms


def add_initial_opinions(g, nodes:int, issues:int, communities:int, p_agree:float, seeds_per_community_ratio:float, seed=None):
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    g.add_vertices(issues)

    for i in range(nodes, nodes + issues):
        g.vs[i]['node_type'] = 'issue'
        g.vs[i]['issue_name'] = f"Issue_{i - nodes + 1}"
        g.vs[i]['community'] = -1 # -1 means community does not apply to issues
    
    opinion_edges = []
    opinion_values = []
    platforms = assign_initial_platforms(issues, p_agree, seed)

    community_sizes = {}
    for c in range(communities):
        actors = [v.index for v in g.vs if v['node_type'] == 'actor' and v['community'] == c]
        community_sizes[c] = len(actors)
        
    # Sort communities by size descending
    sorted_communities = sorted(community_sizes.items(), key=lambda item: item[1], reverse=True)
    
    # Grab the IDs of the top 2 communities
    target_communities = []
    if len(sorted_communities) >= 2:
        target_communities = [sorted_communities[0][0], sorted_communities[1][0]]
    elif len(sorted_communities) == 1:
        target_communities = [sorted_communities[0][0]] 

  
    for c in range(communities): 
       
        if c not in target_communities:
            continue
            
       
        platform_id = 0 if c == target_communities[0] else 1
        
        actors = [v.index for v in g.vs if v['node_type'] == 'actor' and v['community'] == c]
        actual_seeds_count = np.ceil(len(actors) * seeds_per_community_ratio)
        seeds = random.sample(actors, int(actual_seeds_count))
        
        for seed_actor in seeds:
            for issue_idx in range(issues):
                issue_node_id = nodes + issue_idx
                opinion_edges.append((seed_actor, issue_node_id))
                opinion_values.append(platforms[platform_id][issue_idx])
    
   
    start = g.ecount() 
    g.add_edges(opinion_edges)
    for i in range(start, g.ecount()):
        g.es[i]['edge_type'] = 'attitude'
        g.es[i]['opinion_val'] = opinion_values[i - start]
    # for c in range(communities): 
    #     actors = [v.index for v in g.vs if v['node_type'] == 'actor' and v['community'] == c]
        
    #     actual_seeds_count = np.ceil(len(actors) * seeds_per_community_ratio)
    #     seeds = random.sample(actors, int(actual_seeds_count))
        
    #     for seed_actor in seeds:
    #         for issue_idx in range(issues):
    #             issue_node_id = nodes + issue_idx
    #             opinion_edges.append((seed_actor, issue_node_id))
    #             opinion_values.append(platforms[c][issue_idx])
    
    # start = g.ecount() # before adding new edges
    # g.add_edges(opinion_edges)
    # for i in range(start, g.ecount()):
    #     g.es[i]['edge_type'] = 'attitude'
    #     g.es[i]['opinion_val'] = opinion_values[i - start]
    
    return g


def add_initial_opinions_new(g, nodes: int, issues: int, communities: int, p_agree: float, seeds_per_community_ratio: float, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
   
    g.add_vertices(issues)
    for i in range(nodes, nodes + issues):
        g.vs[i]['node_type'] = 'issue'
        g.vs[i]['issue_name'] = f"Issue_{i - nodes + 1}"
        g.vs[i]['community'] = -1 
    
    opinion_edges = []
    opinion_values = []
    platforms = assign_initial_platforms(issues, p_agree, seed) 

    
    for v in g.vs:
        if v['node_type'] == 'actor':
            v['threshold'] = random.uniform(0.05, 0.33)

   
    community_platform_mapping = {c: 0 if c % 2 == 0 else 1 for c in range(communities)}

    for c in range(communities): 
        platform_id = community_platform_mapping[c]
        actors = [v.index for v in g.vs if v['node_type'] == 'actor' and v['community'] == c]
        
        actual_seeds_count = max(1, int(np.ceil(len(actors) * seeds_per_community_ratio)))
        if not actors:
            continue
            
        
        seeds = random.sample(actors, actual_seeds_count)
        
        for seed_actor in seeds:
            for issue_idx in range(issues):
                issue_node_id = nodes + issue_idx
                opinion_edges.append((seed_actor, issue_node_id))
                opinion_values.append(platforms[platform_id][issue_idx])
    
    
    start = g.ecount() 
    g.add_edges(opinion_edges)
    for i in range(start, g.ecount()):
        g.es[i]['edge_type'] = 'attitude'
        g.es[i]['opinion_val'] = opinion_values[i - start]
    
    return g

