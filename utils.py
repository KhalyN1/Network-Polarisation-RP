import random
import igraph as ig
from igraph import Graph

def opinion_split_2_communities(issues, p_agree=0.5):
    """
    Split communities into two groups with opposing opinions on some issues.
    """
    splits = {0: {}, 1: {}}
    for i in range(issues):
        stance = random.choice([-1, 1])
        splits[0][i] = stance
        if random.random() < p_agree:
            splits[1][i] = stance
        else:
            splits[1][i] = -stance
    return splits



def opinion_split_3_communities(issues):
    """
    Split communiites, have 3 different splits, each agreeing on about 2/3 of the issues.
    """
    split_1 = issues // 3
    split_2 = 2 * (issues // 3)
    
    splits = {0: {}, 1: {}, 2: {}}
    
    for i in range(issues):
        if i < split_1:
            splits[0][i], splits[1][i], splits[2][i] = 1, 1, -1
        elif i < split_2:
            splits[0][i], splits[1][i], splits[2][i] = -1, 1, 1
        else:
            splits[0][i], splits[1][i], splits[2][i] = 1, -1, 1
            
    return splits

def get_cross_density(g):
   
    social_edges = g.es.select(edge_type='social')
    total_edges = len(social_edges)

    cross_edges = 0
    for e in g.es.select(edge_type='social'):
        if g.vs[e.source]['community'] != g.vs[e.target]['community']:
            cross_edges += 1
            
    return cross_edges / total_edges if total_edges > 0 else 0
