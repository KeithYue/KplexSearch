# coding=utf-8
import snap

def maximal_kplex(compsub, candidate, _not):
    '''
    compsub: current k-plex
    candidate: candidates who are extendible to compsub
    return: all maximal k-plex containing q
    '''
    if len(candidate) == 0 and len(_not) == 0:
        yield compsub
    else:
        # candidate not none, then do the DFS

def test():
    pass

if __name__ == '__main__':
    test()
