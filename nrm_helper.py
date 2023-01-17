import networkx as nx
import math
import numpy as np
import pandas as pd
import helper
np.seterr(divide='ignore', invalid='ignore')    #ignores the division by zero (OR value tending to zero)

def divide(a, b):
    '''
    INPUT : two numbers a and b
    OUTPUT: a/b (a divided by b)
    
    divide two numbers using log because if the denominator is two
    low numpy will give warning of dividing by zero. converting to log then
    applying antilog will give same result (i.e. a/b ) with no warnings.

    divisions in the below code (eg-line number 84-87) can be done using this function
    instead of dividing directly.
    '''
    loga = np.log10(a)
    logb = np.log10(b)
    diff = loga-logb
    return 10**diff

def compute_katz(graph):
    '''
    Returns an array of Katz Centrality for each node of the Graph
    
    TIME COMPLEXITY - O(V^2)*max_iteration => O(V^2) where V = no of nodes.
    '''
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:

        G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])

    # phi = (1+math.sqrt(graph.nodes+1000))/2.0 # largest eigenvalue of adj matrix
    # centrality = nx.katz_centrality(G,1/phi-0.01, max_iter=sys.maxsize, tol=1.0e-6)
    centrality = nx.katz_centrality(G)  #Time complexity - O(V^2)*max_iteration => O(V^2)
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    #print(centrality)
    return centrality


def compute_strength(graph):
    strength = [0 for _ in range(graph.nodes)]
    for u in range(graph.nodes):
        for v in graph.neighbours[u]:
            strength[u] += graph.edge_weights[(str(u), str(v))]
    return np.array(strength)

# Time complexity O(V^2) ; V=no of nodes
def get_ranks(graph):
    nrm = dict()
    strength = compute_strength(graph)
    for i in range(graph.nodes):
        #nrm[i] = ((graph.node_weights[i])+(graph.node_weights[i])) * strength[i]
        nrm[i] = 2*(graph.node_weights[i]) * strength[i]
    ranks = sorted(  # array containing weights
        [i for i in range(graph.nodes)], key=lambda x: nrm[x], reverse=True
    )
    return ranks


# weight calculation using shanon entropy method
# Time complexity O(V) v = no of nodes
def get_weights(data, nodes):
    column_sums = data.sum(axis=0)
    normalized = (
        data / column_sums[:, np.newaxis].transpose()
    )  # normalizing the attribute values
    E_j = normalized * np.log(normalized)
    column_sum = np.sum(E_j, axis=0)
    k = 1 / np.log(nodes)
    column_sum = -k * column_sum
    column_sum = 1 - column_sum
    E_j_column_sum = sum(column_sum)
    w_j = column_sum / E_j_column_sum  # calculated weight array
    return w_j


if __name__ == "__main__":
    substrate, vne_list = helper.read_pickle()
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(substrate.nodes))
    for edge in substrate.edges:
        G.add_edge(int(edge[0]), int(edge[1]), weight=substrate.edge_weights[edge])
    phi = (1 + math.sqrt(substrate.nodes + 1)) / 2.0  # largest eigenvalue of adj matrix