
import random

def simulate_network_evolution(g, nodes: int, issues: int, steps: int = 10, p_rewire: float = 0.05):
    
    actors = [v.index for v in g.vs if v['node_type'] == 'actor']
    
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
                                g.delete_edges(existing_edge)
                                social_network[actor].discard(friend)
                                social_network[friend].discard(actor)
                                social_neighbors.remove(friend)
                                changes_this_step += 1
                                
                                # Find a new friend who doesn't oppose on this issue
                                non_friends = set(actors) - social_network[actor] - {actor, friend}
                                valid_targets = [
                                    tgt for tgt in non_friends
                                    if actor_opinions[tgt].get(issue_node, 0) != -current_val
                                ]
                                
                                if valid_targets:
                                    new_friend = random.choice(valid_targets)
                                    g.add_edges([(actor, new_friend)])
                                    new_edge_id = g.ecount() - 1
                                    g.es[new_edge_id]['edge_type'] = 'social'
                                    g.es[new_edge_id]['opinion_val'] = None
                                    social_network[actor].add(new_friend)
                                    social_network[new_friend].add(actor)
                                    social_neighbors.append(new_friend)
                                    
                                    # Update influence counts for new friend
                                    new_friend_op = actor_opinions[new_friend].get(issue_node, 0)
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
                            g.delete_edges(edge_to_delete)
                        if issue_node in actor_opinions[actor]:
                            del actor_opinions[actor][issue_node]
                    
                    if target_val != 0:
                        g.add_edges([(actor, issue_node)])
                        new_edge_id = g.ecount() - 1
                        g.es[new_edge_id]['edge_type'] = 'attitude'
                        g.es[new_edge_id]['opinion_val'] = target_val
                        actor_opinions[actor][issue_node] = target_val

        if changes_this_step == 0:
            break

    return g