
import random
import igraph as ig

def simulate_network_evolution(g, nodes: int, issues: int, steps: int = 10, p_rewire: float = 0.05):
    
    actors = [v.index for v in g.vs if v['node_type'] == 'actor']
    total_steps = 0
    actor_opinions = {a: {} for a in actors}
    social_network = {a: set() for a in actors}
    
    for e in g.es:
        if e['edge_type'] == 'attitude':
            actor_opinions[e.source][e.target] = e['opinion_val']
        elif e['edge_type'] == 'social':
            social_network[e.source].add(e.target)
            social_network[e.target].add(e.source)

    for step in range(steps):
        random.shuffle(actors)
        changes_this_step = 0
        
        #Use these to avoid constant igraph recomputation 
        edges_to_delete_ids = set() 
        edges_to_add = []
        edge_types_to_add = []
        opinion_vals_to_add = []

        for actor in actors:
            social_neighbors = list(social_network[actor])
            total_friends = len(social_neighbors)
            if total_friends == 0:
                continue
            
            personal_threshold = g.vs[actor]['threshold']
            
            # Now iterate per issue independently
            for issue_idx in range(issues):
                issue_node = nodes + issue_idx
                current_val = actor_opinions[actor].get(issue_node, 0)
                
                # Count influence for THIS issue only
                pos_influence = 0
                neg_influence = 0
                
                for friend in list(social_neighbors):  # copy since we may rewire
                    friend_op = actor_opinions[friend].get(issue_node, 0)
                    
                    if friend_op == 1:
                        pos_influence += 1
                    elif friend_op == -1:
                        neg_influence += 1
                    
                    if current_val != 0 and friend_op == -current_val:
                        if random.random() < p_rewire:

                            existing_edge = g.get_eid(actor, friend, error=False)
                            if existing_edge != -1:
                                edges_to_delete_ids.add(existing_edge)
                                
                                social_network[actor].discard(friend)
                                social_network[friend].discard(actor)
                                social_neighbors.remove(friend)
                                changes_this_step += 1
                                
                                # Find a new friend who doesn't oppose on this issue
                                # non_friends = set(actors) - social_network[actor] - {actor, friend}
                                # valid_targets = [
                                #     tgt for tgt in non_friends
                                #     if actor_opinions[tgt].get(issue_node, 0) != -current_val
                                # ]

                                new_social_neighbor = None

                                # instead of looking through all non-friends, check 50 random nodes
                                for _ in range(50):
                                    candidate = random.choice(actors)
                                    if candidate == actor or candidate in social_network[actor]:
                                        continue

                                    if actor_opinions[candidate].get(issue_node, 0) == current_val:
                                        new_social_neighbor = candidate
                                        break

                                if new_social_neighbor is not None:
                                    edges_to_add.append((actor, social_neighbors))
                                    edge_types_to_add.append('social')
                                    opinion_vals_to_add.append(None)
                                
                                    social_network[actor].add(new_social_neighbor)
                                    social_network[new_social_neighbor].add(actor)
                                    social_neighbors.append(new_social_neighbor)

                                    new_friend_op = actor_opinions[new_social_neighbor].get(issue_node, 0)
                                    if new_friend_op == 1:
                                        pos_influence += 1
                                    elif new_friend_op == -1:
                                        neg_influence += 1
                                
                
                # Opinion update for THIS issue
                total_friends_now = len(social_neighbors)
                if total_friends_now == 0:
                    continue
                    
                frac_pos = pos_influence / total_friends_now
                frac_neg = neg_influence / total_friends_now
                
                target_val = 0
                if frac_pos >= personal_threshold and frac_pos > frac_neg:
                    target_val = 1
                elif frac_neg >= personal_threshold and frac_neg > frac_pos:
                    target_val = -1
                
                # Apply opinion change for THIS issue
                if target_val != current_val:
                    if current_val != 0 and random.random() > 0.5:
                        continue

                    changes_this_step += 1
                    
                    if current_val != 0:
                        edge_to_delete = g.get_eid(actor, issue_node, error=False)
                        if edge_to_delete != -1:
                           edges_to_delete_ids.add(edge_to_delete)
                        if issue_node in actor_opinions[actor]:
                            del actor_opinions[actor][issue_node]
                    
                    if target_val != 0:
                        edges_to_add.append((actor, issue_node))
                        edge_types_to_add.append('attitude')
                        opinion_vals_to_add.append(target_val)
                        actor_opinions[actor][issue_node] = target_val


        if edges_to_delete_ids:
            g.delete_edges(list(edges_to_delete_ids))
            
        if edges_to_add:
            g.add_edges(edges_to_add)
            start_idx = g.ecount() - len(edges_to_add)
            for i in range(len(edges_to_add)):
                g.es[start_idx + i]['edge_type'] = edge_types_to_add[i]
                g.es[start_idx + i]['opinion_val'] = opinion_vals_to_add[i]
    
        if changes_this_step == 0:
            break

        total_steps += 1

    #print(f"Total steps taken: {total_steps}, Final changes in last step: {changes_this_step}")
    return g, total_steps

