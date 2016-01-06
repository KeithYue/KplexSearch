# coding=utf-8
import networkx as nx
import random
from lplex_search import dataset, load, neighbors
import time
from pprint import pprint
from multiprocessing import Pool

def k_hop_nbrs(G, k, node):
    '''
    find k-hop neighbors of one single node
    '''
    nbrs = set([node])
    for i in range(0,k):
        new_members = [j for i in nbrs for j in G.neighbors(i)]
        nbrs.update(new_members)
    nbrs.difference_update(set([node]))
    return nbrs

def k_hop_nbrs_n(G, k , nbunch):
    '''
    return the k-hop neighbors of nbunch
    '''
    res = k_hop_nbrs(G, k, nbunch[0])
    for i in nbunch[1:]:
        res.intersection_update(k_hop_nbrs(G,k,i))
    return res

def minimum_degree(G):
    '''
    return the minimum degree of G
    '''
    return min(list(nx.degree(G, G.nodes()).values()))

def remove_by_degree(G, d):
    '''
    remove nodes by degree
    '''
    nodes_to_be_delete = [i for i in G.nodes() if nx.degree(G, i) < d]
    while len(nodes_to_be_delete) > 0:
        print(nodes_to_be_delete)
        if 164373 in nodes_to_be_delete:
            a = input()
        G.remove_nodes_from(nodes_to_be_delete)
        nodes_to_be_delete = [i for i in G.nodes() if nx.degree(G, i) < d]
    return


# the structure of the optimal solution
optimal = set()
count = 0
def BB(G, k, set_a, block, cores=None, select_method='rand'):
    '''
    The bound and branch for maximized k-plex problem
    a: LHS set of nodes, an already found k-plex
    b: nodes need to be explored
    select_method: selection method, default is random method
    pw_dist: pair distance
    '''
    # some nodes in a may be not in graph
    global optimal, count
    count += 1

    # check whether all node are in graph

    a = set(set_a)

    c = set(block)
    b = cand_gen(G, k, a, c, cores)
    # if len(b) < len(optimal) - len(a):
    #     return

    # calculate the connected component, this part is togged to
    gb = nx.subgraph(G, b)
    connected_comp_gb = nx.connected_components(gb)
    b = []
    for comp in connected_comp_gb:
        if len(comp) >= len(optimal) - len(a):
            b.extend(comp)

    print('num of call:', count)
    # print('now cand', a)
    # print('block', block)
    # print('neighbor size', len(b))
    print(a, b)

    while len(b) > 0:
        opt_index = cand_select(G, k, a, b, select_method)
        v = b.pop(opt_index)
        a_plus = set(a)
        a_plus.add(v)
        c.add(v)
        # the current solution is validate
        if upper_bound(G, k, a_plus) < len(optimal):
            continue
        if len(a_plus) > len(optimal):
           optimal = set(a_plus)
           # remove_by_degree(G, len(optimal)-k)
        BB(G, k , a_plus,c, cores, select_method)

def cand_select(G, k, a, b, method):
    '''
    select best branch from b to work on first
    b: a list
    method: type of selection of neighbors
    return the index to be remove from b
    '''
    opt_index = 0
    if method == 'rand':
        opt_index =  random.randint(0, len(b)-1)
    return opt_index




def cand_gen(G, k, a, c, cores=None):
    '''
    generate all the branch given a k-plex a
    a: current k-plex
    c: the block
    '''
    b = neighbors(G, a)
    b.difference_update(c)

    # the strict nodes
    subg = G.subgraph(a)
    strict_nodes = {node for node in a if nx.degree(subg, node) == len(a)-k }
    for node in strict_nodes:
        b.intersection_update(G.neighbors(node))


    # always reshape by optimal
    if cores is None:
        b = {node for node in list(b) if nx.degree(G, node) >= len(optimal)-k}
    else:
        b = {node for node in list(b) if cores[node]>=len(optimal)-k}

    # calculate the valid candidates
    b = {node for node in b if len(set(G.neighbors(node)).intersection(a)) >= len(a)+1-k }

    # sort the candidate list
    b = list(b)
    # b.sort(key = lambda x: len(set(G.neighbors(x)).intersection(a)), reverse=True)

    return b

def upper_bound(G, k, H):
    '''
    the upper bound of size of k-plex of H in G
    '''
    # upper_bound_by_deg = min([nx.degree(G, node) for node in H]) + k
    # upper_bound_by_deg = 100

    subg = nx.subgraph(G, H)
    validate_neighbors = {node for node in neighbors(G, H) if len(set(G.neighbors(node)).intersection(H)) >= len(H)+1-k}

    strict_nodes = [node for node in H if len(subg[node]) == len(H)-k]
    if len(strict_nodes) > 0:
        avaliable_nodes = {node for node in G.neighbors(strict_nodes[0]) if node not in H}
        for i in range(1, len(strict_nodes)):
            avaliable_nodes.intersection_update({node for node in G.neighbors(strict_nodes[i]) if node not in H})
        avaliable_nodes.intersection_update(validate_neighbors)

        return len(H)+len(avaliable_nodes)
    else:
        min_d = float('inf')
        for node in H:
            nbrs = neighbors(G, [node])
            nbrs.intersection_update(validate_neighbors)
            num_non_nbrs = k-1-(subg.number_of_nodes() - nx.degree(subg, node))
            min_d = min(min_d, len(nbrs)+num_non_nbrs)
        return min_d



def bound_branch(G, k ,q_nodes, is_use_cores=False, select_method='rand'):
    '''
    wrapper of branch and bound method
    '''
    ts = time.time()
    global optimal
    optimal = set()
    k_neighbors = k_hop_nbrs_n(G, k, q_nodes)
    sub = set(q_nodes)
    sub.update(k_neighbors)
    g = nx.subgraph(G, sub)

    if is_use_cores:
        cores = nx.core_number(g)
    else:
        cores = None

    # print('subgraph ', g.nodes())
    print('minimum degree of subgraph', minimum_degree(g))
    print('k neighbors', len(k_neighbors))
    BB(g, k, q_nodes, set(), cores, select_method)
    print('the solution is', optimal)

    te = time.time()

    texe = round(te-ts, 2) # the execution time

    return texe

def rand_greedy(paras):
    g, k, nodes  = paras
    t1 = bound_branch(g, k, nodes, False, 'rand')
    t2 = bound_branch(g, k, nodes, False, 'greedy')
    return t1, t2

def test():
    g = load(dataset['dblp'])
    t = bound_branch(g, 3, [61], False, 'rand')
    print(t)
    # paras = []
    # for i in range(1,50):
    #     try:
    #         node = random.randint(1, 5000)
    #         neighbor = random.choice(g.neighbors(node))
    #         paras.append((g, 4, [node, neighbor]))
    #     except Exception as e:
    #         print(e)
    #         continue
    # pool = Pool()
    # r_list = pool.map(rand_greedy, paras)
    # pool.close()
    # pool.join()

    # print('rand', 'greedy')
    # for i in range(0, len(r_list)):
    #     print(paras[i][-1], r_list[i])

if __name__ == '__main__':
    # print('test')
    test()
