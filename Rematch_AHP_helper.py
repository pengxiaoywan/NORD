import networkx as nx
import math
import numpy as np
import pandas as pd
import helper
np.seterr(divide='ignore', invalid='ignore')    #ignores the division by zero (OR value tending to zero)


# wITH kATZ
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

def normalize_mat(a):
    a = a*a
    column_sum = np.sqrt(np.sum(a, axis=0))
    return a/column_sum

def compute_katz(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:

        G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])

    # phi = (1+math.sqrt(graph.nodes+1000))/2.0 # largest eigenvalue of adj matrix
    # centrality = nx.katz_centrality(G,1/phi-0.01, max_iter=sys.maxsize, tol=1.0e-6)
    centrality = nx.katz_centrality(G, max_iter = 10000)
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    return centrality

def convt_dict(graph):
    graph = graph.neighbours
    network = {}
    for key, value in graph.items():
        network[key] = [int(i) for i in value]
    return network

def compute_bw(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])
    centrality = nx.betweenness_centrality(G)
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    return centrality

def compute_eigen(graph):
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(graph.nodes))
    for edge in graph.edges:
        G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])
    centrality = nx.eigenvector_centrality(G, max_iter = 10000)
    centrality = np.array([centrality[i] for i in range(graph.nodes)])
    return centrality


def compute_strength(graph):
    strength = [0 for _ in range(graph.nodes)]
    for u in range(graph.nodes):
        for v in graph.neighbours[u]:
            strength[u] += graph.edge_weights[(str(u), str(v))]
    return np.array(strength)

def topsis_ranking(graph_dict, graph, weight_mx, _perf_mx):
#get weighted normalized matirx
    weighted_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(graph.nodes)]
    for i in range(len(_perf_mx)):
      for k in range(len(weight_mx)):
        weighted_nor_mx[i][k] = _perf_mx[i][k] * weight_mx[k]

    # get max and min of column matrix
    max_list = list(map(max, zip(*weighted_nor_mx)))
    min_list = list(map(min, zip(*weighted_nor_mx)))

    ## max_list - weighted_nor_mx
    max_weight_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(graph.nodes)]
    min_weight_nor_mx = [[0, 0, 0, 0, 0, 0] for i in range(graph.nodes)]
    for i in range(len(weighted_nor_mx)):
      for k in range(len(max_list)):
        max_weight_nor_mx[i][k] = max_list[k] - weighted_nor_mx[i][k]
        min_weight_nor_mx[i][k] = min_list[k] - weighted_nor_mx[i][k]

    s_plus_mx = [[] for i in range(graph.nodes)]
    for _idx in range(len(max_weight_nor_mx)):
      s_plus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                      max_weight_nor_mx[_idx]))]
    s_minus_mx = [[] for i in range(graph.nodes)]
    for _idx in range(len(min_weight_nor_mx)):
      s_minus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                       min_weight_nor_mx[_idx]))]
    ## s_plus_mx + s_minus_mx
    s_plus_plus = [[0] for i in range(1, graph.nodes+1)]
    for i in range(len(s_plus_mx)):
      for k in range(len(s_plus_plus[i])):
        s_plus_plus[i][k] = s_plus_mx[i][k] + s_minus_mx[i][k]
    s_plus_plus_dict = {}
    vertices = graph_dict.keys()
    for idx, k in enumerate(vertices):
      s_plus_plus_dict[k] = s_plus_plus[idx][0]

    ## get rank values
    rank_dict = {}
    for idx, k in enumerate(vertices):
      # rank_dict[k] = s_minus_mx[idx][0]/s_plus_plus[idx][0]
      rank_dict[k] = 0 if (s_minus_mx[idx][0] == 0 and s_plus_plus[idx][0] ==
                           0) else s_minus_mx[idx][0]/s_plus_plus[idx][0]
    ## generate rank for nodes
    node_rank = {key: rank for rank, key in enumerate(sorted(rank_dict,
                                                             key=rank_dict.get, reverse=True), 1)}
    return sorted([i for i in range(len(node_rank))], key = lambda x: node_rank[x])

def get_ranks(graph):
    static_mat = np.array([[1,1/9], [9,1]])
    static_mat = static_mat/np.sum(static_mat, axis=0)
    static_mat = np.average(static_mat, axis=1)
    option_mat = np.array([[graph.node_weights[i] for i in range(graph.nodes)], [graph.node_weights[i] for i in range(graph.nodes)]])
    option_mat = option_mat/option_mat.sum(axis=1)[:,None]
    option_mat = option_mat*static_mat[:, np.newaxis]
    option_mat = np.sum(option_mat, axis=0)
    ranking = sorted([i for i in range(graph.nodes)], key=lambda x: option_mat[x])
    return ranking

# weight calculation using shanon entropy method
def get_weights(data, nodes):
    column_sums = data.sum(axis=0)
    normalized = (
        data / column_sums[:, np.newaxis].transpose()
    )  # normalizing the attribute values
    normalized[np.isnan(normalized)] = 0
    # normalized = np.zeros(data.shape)
    # for i in range(data.shape[0]):
    #     for j in range(data.shape[1]):
    #         if column_sums[j] != 0:
    #             normalized[i,j] = data[i,j]/column_sums[j]
    E_j = np.zeros(normalized.shape)
    # for i in range(normalized.shape[0]):
    #     for j in range(normalized.shape[1]):
    #         if normalized[i, j] != 0:
    #             E_j[i, j] = normalized[i, j] * math.log(normalized[i, j])
    E_j = normalized * np.log(normalized)
    E_j[np.isnan(E_j)] = 0
    column_sum = np.sum(E_j, axis=0)
    k = 1 / np.log(nodes)
    column_sum = -k * column_sum
    column_sum = 1 - column_sum
    E_j_column_sum = sum(column_sum)
    w_j = column_sum / E_j_column_sum  # calculated weight array
    #print(f"Sum:{sum(w_j)}")
    return w_j


if __name__ == "__main__":
    substrate, vne_list = helper.read_pickle()
    G = nx.Graph()
    G.add_nodes_from(nx.path_graph(substrate.nodes))
    for edge in substrate.edges:
        G.add_edge(int(edge[0]), int(edge[1]), weight=substrate.edge_weights[edge])
    phi = (1 + math.sqrt(substrate.nodes + 1)) / 2.0  # largest eigenvalue of adj matrix
    #print(nx.katz_centrality(G, max_iter=1000, tol=1.0e-6))
