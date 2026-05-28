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


def assign_initial_platforms(communities:int, issues:int, p_agree:float, seed=None):
    if random.seed is not None:
        random.seed(seed)
    
    platforms = {}
    
    base_profile = [random.choice([1, -1]) for _ in range(issues)] #each community has base opinion for initializing actors
    
    for c in range(communities):
        platforms[c] = {}
        for issue_idx in range(issues):
            if random.random() < p_agree:
                platforms[c][issue_idx] = base_profile[issue_idx]
            else:
                platforms[c][issue_idx] = random.choice([1, -1])
                
    return platforms


def add_initial_opinions(g, nodes:int, issues:int, communities:int, p_agree:float, seeds_per_community:int, seed=None):

    if random.seed is not None:
        random.seed(seed)
    
    g.add_vertices(issues)

    for i in range(nodes, nodes + issues):
        g.vs[i]['node_type'] = 'issue'
        g.vs[i]['issue_name'] = f"Issue_{i - nodes + 1}"
        g.vs[i]['community'] = -1 # -1 means community does not apply to issues
    
    opinion_edges = []
    opinion_values = []
    platforms = assign_initial_platforms(communities, issues, p_agree, seed)

    for c in range(communities): 
        actors = [v.index for v in g.vs if v['node_type'] == 'actor' and v['community'] == c]
        
        actual_seeds_count = min(len(actors), seeds_per_community)
        seeds = random.sample(actors, actual_seeds_count)
        
        for seed_actor in seeds:
            for issue_idx in range(issues):
                issue_node_id = nodes + issue_idx
                opinion_edges.append((seed_actor, issue_node_id))
                opinion_values.append(platforms[c][issue_idx])
    
    start = g.ecount() # before adding new edges
    g.add_edges(opinion_edges)
    for i in range(start, g.ecount()):
        g.es[i]['edge_type'] = 'attitude'
        g.es[i]['opinion_val'] = opinion_values[i - start]
    
    return g

def add_issues_and_opinions(g, nodes:int=50, communities:int=2, issues:int=4, opinion_density:float=0.8, seed=None, p_agree:float=0.1, alignment_prob:float=0.75):
    ''' 
    Mostly placeholder, initializes network with fully formed opinions, no evolution for now.
    '''
    if random.seed is not None:
        random.seed(seed)
        
    #add issue nodes
    g.add_vertices(issues)
    
    for i in range(nodes, nodes + issues):
        g.vs[i]['node_type'] = 'issue'
        g.vs[i]['issue_name'] = f"Issue_{i - nodes + 1}"
        g.vs[i]['community'] = -1 # -1 means community does not apply to issues
        
    
    opinion_edges = []
    opinion_values = []
    splits = {}
    if communities == 2:
        splits = opinion_split_2_communities(issues, p_agree)
    elif communities == 3:
        splits = opinion_split_3_communities(issues)
    
    # Embed political opinion in communities (placeholder as we don't have homophily and evolution yet)
    # WILL BE CHANGED
    for actor_id in range(nodes):
        actor_comm = g.vs[actor_id]['community']
        
        for issue_id in range(nodes, nodes + issues):
    
            if random.random() < opinion_density:
                opinion_edges.append((actor_id, issue_id))
                
                comm_opinion = splits[actor_comm][issue_id - nodes]
                
                # align opinion with community with some probability, more realistic probably 
                if random.random() < alignment_prob:
                    opinion_values.append(comm_opinion)
                else:
                    opinion_values.append(-comm_opinion) 
                
    starting_edge_count = g.ecount()
    g.add_edges(opinion_edges)
    
    
    for i in range(starting_edge_count, g.ecount()):
        g.es[i]['edge_type'] = 'attitude'
        g.es[i]['opinion_val'] = opinion_values[i - starting_edge_count]
    
    return g
    