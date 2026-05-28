import itertools
import random

from igraph import Graph 
def measure_network_polarization(g):
    """
    Measures the relational and ideological polarization metrics from Mepham et. al.
    """
 
    actors = [v.index for v in g.vs.select(node_type='actor')]
  
    opinions = {a: {} for a in actors}
    for edge in g.es.select(edge_type='attitude'):
        if edge.source in opinions:
            opinions[edge.source][edge.target] = edge['opinion_val']

   
    social_edges = set()
    for edge in g.es.select(edge_type='social'):
        social_edges.add((edge.source, edge.target))

    def are_tied(u, v):
        return (u, v) in social_edges or (v, u) in social_edges

   
    tied_agree = 0
    total_agree = 0
    not_tied_disagree = 0
    total_disagree = 0

   
    consistent_agree = 0
    consistent_disagree = 0
    inconsistent = 0

    
    for i, j in itertools.combinations(actors, 2):
       
        common_issues = set(opinions[i].keys()).intersection(set(opinions[j].keys()))
        if not common_issues:
            continue
            
        tied = are_tied(i, j)
        agreements_list = [] 

    
        for issue in common_issues:
            agrees = (opinions[i][issue] == opinions[j][issue])
            agreements_list.append(agrees)

            if agrees:
                total_agree += 1
                if tied:
                    tied_agree += 1
            else:
                total_disagree += 1
                if not tied:
                    not_tied_disagree += 1

        
        if len(common_issues) >= 2:
        
            for a1, a2 in itertools.combinations(agreements_list, 2):
                if a1 and a2:
                    consistent_agree += 1      # Agree on both issues
                elif not a1 and not a2:
                    consistent_disagree += 1   # Disagree on both issues
                else:
                    inconsistent += 1          # Agree on one, disagree on the other

    
    relational_attraction = tied_agree / total_agree if total_agree > 0 else 0
    relational_repulsion = not_tied_disagree / total_disagree if total_disagree > 0 else 0

    ideo_attr_denom = consistent_agree + inconsistent
    ideological_attraction = consistent_agree / ideo_attr_denom if ideo_attr_denom > 0 else 0

    ideo_rep_denom = consistent_disagree + inconsistent
    ideological_repulsion = consistent_disagree / ideo_rep_denom if ideo_rep_denom > 0 else 0

   
    relational_polarization = (relational_attraction + relational_repulsion) / 2
    ideological_polarization = (ideological_attraction + ideological_repulsion) / 2
    network_polarization = (relational_polarization + ideological_polarization) / 2

    return {
        'relational_attraction': relational_attraction,
        'relational_repulsion': relational_repulsion,
        'relational_polarization': relational_polarization,
        'ideological_attraction': ideological_attraction,
        'ideological_repulsion': ideological_repulsion,
        'ideological_polarization': ideological_polarization,
        'network_polarization': network_polarization
    }


