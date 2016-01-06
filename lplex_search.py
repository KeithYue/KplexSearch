# coding=utf-8
# load the graph data

import networkx as nx
import logging
import matplotlib.pyplot as plt
import random
import time
from cProfile import Profile, runctx
from pstats import Stats
from pprint import pprint
from collections import deque
from itertools import product
logging.basicConfig(level=logging.DEBUG)

dataset = dict(
        dblp = './data/com-dblp.ungraph.txt',
        test = './data/test.txt',
        test2 = './data/test2.txt',
        test4 = './data/test4.txt'
        )

def load(data_file):
    '''
    load data from txt file
    return a graph instance
    '''
    logging.info('loading the graph')
    g = nx.Graph()
    with open(data_file) as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            s, t = line.split()
            g.add_edge(int(s),int(t))
    logging.info('loading complete')
    return g

def is_kplex(H, G, k):
    '''
    test whether H is a k-plex in G
    '''
    sub = G.subgraph(H)
    for node in sub:
        if sub.degree(node) < len(sub) - k:
            # print(node, sub.degree(node), len(sub))
            return False
    return True


def neighbors(G, H):
    '''
    compute neighbors of H in G
    rtype: set of nodes
    '''
    neighbors = set()
    for node in H:
        ns = G.neighbors(node)
        neighbors.update(ns)
    neighbors.difference_update(set(H))
    return neighbors

maximal_search_count = 0
def maximal_search(G, k, results, compsub, candidate, _not):
    '''
    G: the whole graph
    compsub: current k-plex
    candidate: extendible candidte
    _not: explored previously
    '''
    global Results, maximal_search_count
    maximal_search_count += 1
    print('num of count', maximal_search_count)
    if len(candidate) == 0 and len(_not) == 0:
        # print('I have found a k-plex:', compsub)
        # yield compsub
        results.append(compsub)

    if len(candidate) == 0 and len(_not) > 0:
        # compsub can not be extended
        return
    X = _not.copy()
    while len(candidate) > 0:
        # R, P, X
        v = candidate.pop()
        R = compsub.copy()
        R.add(v)

        P = set()
        for node in neighbors(G, R):
            if is_kplex(R.union(set([node])), G, k):
                P.add(node)
        # compute the neighbors of R
        # for i in R:
        #     for j in G.neighbors(i):
        #         if j not in R:
        #             P.add(j)
        # subg = G.subgraph(R)

        # # filter out P
        # trivial_nodes = [ node for node in subg.nodes() if len(subg[node]) == len(R) - k]
        # for i in trivial_nodes:
        #     P.intersection_update(G.neighbors(i))

        # P = set([i for i in P if len(set(G.neighbors(i)).intersection(R)) >= len(R) + 1 - k])
        _X = X.intersection(P)
        # remove nodes in X
        for node in _X:
            P.discard(node)

        maximal_search(G, k, results, R, P, _X)


        X.add(v)

def local_expand(G, k, q_nodes):
    '''
    G: graph
    k: k-plex
    q_nodes: the query nodes
    '''
    q = q_nodes[0] # choose one of the query nodes
    r = []
    maximal_search(G, k, r, set([q]), set(G.neighbors(q)), set())
    max_size = 0
    optimal = []
    # print(r)
    for i in r:
        if len(i) > max_size and set(q_nodes).issubset(i):
            max_size = len(i)
    for i in r:
        if len(i) == max_size and set(q_nodes).issubset(i):
            optimal.append(i)
    return optimal

def bunch_expand(G, k, q_nodes):
    '''
    instead of starting with one single query node
    feed all the q_nodes
    '''
    r = []
    Q_neighbors = []
    for i in neighbors(G, q_nodes):
        tmp = set(q_nodes)
        tmp.add(i)
        if is_kplex(tmp, G, k):
            Q_neighbors.append(i)

    maximal_search(G, k, r, set(q_nodes), set(Q_neighbors), set())
    max_size = 0
    optimal = []
    # print(r)
    r = [sub for sub in r if nx.is_connected(G.subgraph(sub))]
    for i in r:
        if len(i) > max_size and set(q_nodes).issubset(i):
            max_size = len(i)
    for i in r:
        if len(i) == max_size and set(q_nodes).issubset(i):
            optimal.append(i)
    return optimal

def greedy_plex(G, k, q_nodes):
    '''
    gready select the nodes
    '''



Results = []

def test():
    g =  load(dataset['dblp'])
    # # print('kpath')
    # runctx('r = bunch_expand(g, 3, [1,2]);print(r, len(r))', globals(), locals())

    # print('local expand')
    # runctx('r=local_expand(g, 3, [1,2]);print(r, len(r))', globals(), locals())
    r = bunch_expand(g, 3, [2])
    print(r, len(r))

    # print(results)
    # for i in range(1, 9):
    #     print('the {}-plex:'.format(i))
    #     r = []
    #     maximal_search(g, i, r, set([4]), set(g.neighbors(4)), set())
    #     if len(r) != 0:
    #         print(r)
    #     else:
    #         break
    # print('searching for node 4')
    # results  = local_expand(g, 4, [6,8])
    # print('The optimal solution: ')
    # pprint(results)
    # pass

if __name__ == '__main__':
    test()
    # print(nx.shortest_path(g, 6,9))
    # print(is_kplex([1,2,6,7], g, 3))
    # r = bunch_expand(g, 3, [1,8])
    # print('optimal solution: ', r)
