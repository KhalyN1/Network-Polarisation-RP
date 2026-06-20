from igraph import Graph

def get_cross_density(g: Graph) -> float:
   
    social_edges = g.es.select(edge_type='social')
    total_edges = len(social_edges)

    cross_edges = 0
    for e in g.es.select(edge_type='social'):
        if g.vs[e.source]['community'] != g.vs[e.target]['community']:
            cross_edges += 1
            
    return cross_edges / total_edges if total_edges > 0 else 0
