

from random import random


def simulate_network_evolution(g, nodes:int, issues:int, threshold:float=0.5, steps:int=10):
   
    #if random.seed is not None:
    #    random.seed(seed)
    edges_before = g.ecount()

    for i in range(steps):
        actors = [v.index for v in g.vs if v['node_type'] == 'actor']
        
    
        current_opinions = {a: {} for a in actors}
        for e in g.es.select(edge_type='attitude'):
            current_opinions[e.source][e.target] = e['opinion_val']
            
        edges_to_remove = []
        new_edges = []
        new_vals = []
        
        for actor in actors:
            neighbors = g.neighbors(actor, mode="all")
            social_neighbors = [n for n in neighbors if g.vs[n]['node_type'] == 'actor']
            total_friends = len(social_neighbors)
            
            if total_friends == 0:
                continue
                
            for issue_idx in range(issues):
                issue_node = nodes + issue_idx
                current_val = current_opinions[actor].get(issue_node, 0)
                
            
                pos_influence, neg_influence = 0, 0
                for friend in social_neighbors:
                    friend_op = current_opinions[friend].get(issue_node, 0)
                    if friend_op == 1: pos_influence += 1
                    elif friend_op == -1: neg_influence += 1
                
                frac_pos = pos_influence / total_friends
                frac_neg = neg_influence / total_friends
                
            
                target_val = 0
                if frac_pos >= threshold and frac_pos > frac_neg:
                    target_val = 1
                elif frac_neg >= threshold and frac_neg > frac_pos:
                    target_val = -1
                    
                # If their mind needs to change, log it for updates
                if target_val != current_val:
                    if current_val != 0:
                        # Find and mark old edge for deletion
                        existing_edge = g.get_eid(actor, issue_node, error=False)
                        if existing_edge != -1:
                            edges_to_remove.append(existing_edge)
                    
                    if target_val != 0:
                        new_edges.append((actor, issue_node))
                        new_vals.append(target_val)
                        
        # Batch purge flipped edges and batch add updated edges
        if edges_to_remove:
            g.delete_edges(list(set(edges_to_remove)))
            
        start_edges = g.ecount()
        g.add_edges(new_edges)
        for i in range(start_edges, g.ecount()):
            g.es[i]['edge_type'] = 'attitude'
            g.es[i]['opinion_val'] = new_vals[i - start_edges]
        
        if edges_before == g.ecount():
            break

    return g
   