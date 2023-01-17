import math
import numpy
import networkx as nx
import logging
log=logging
class WeightMatrix(object):
  def __init__(self, network, crb, bandwidth, betweenness, eigen, degree):
    self.network = network
    self.crb = crb
    self.bandwidth = bandwidth
    self.betweenness = betweenness
    self.eigen = eigen
    self.degree = degree
    self.vertices = network.keys()
    self._perf_mx = []
    self.katz = {}

  def generate_katz(self):
    g = nx.DiGraph(self.network)
    self.katz = nx.katz_centrality(g, max_iter=1000, tol=1.0e-6, normalized=True)
    return self.katz

  def get_katz(self):
    return self.katz

  def get_weight_matrix(self):
    tp_matrix = [[] for i in range(len(self.network))]
    _katz = self.generate_katz()
    for idx, _node in enumerate(self.vertices):
      tp_matrix[idx].append(self.crb[_node])
      tp_matrix[idx].append(self.bandwidth[_node])
      tp_matrix[idx].append(self.betweenness[_node])
      # tp_matrix[idx].append(self.eigen[idx][0])     #if not using inbuilt function
      tp_matrix[idx].append(self.eigen[idx])     #if using using inbuilt eigen vector function
      tp_matrix[idx].append(self.degree[_node])
      #tp_matrix[idx].append(_katz[_node])
      #log.info("The Wight of each attribute is",tp_matrix)
    return tp_matrix

  def compute_performance_indices_matrix(self):
    matrix = self.get_weight_matrix()
    sum_crb, sum_bdwth, sum_bc, sum_eig, sum_dgr, = 0, 0, 0, 0, 0
    for row in matrix:
      sum_crb += row[0]
      sum_bdwth += row[1]
      sum_bc += row[2]
      sum_eig += row[3]
      sum_dgr += row[4]
      #sum_katz += row[5]
    nor_matrix = [[0, 0, 0, 0, 0, 0] for i in range(len(self.network))]
    for idx, _row in enumerate(matrix):
      nor_matrix[idx][0] = round(float(_row[0])/float(sum_crb),3)
      nor_matrix[idx][1] = round(float(_row[1])/float(sum_bdwth),3)
      nor_matrix[idx][2] = round(float(_row[2])/float(sum_bc),3) if sum_bc \
                                                                    !=0 else 0
      nor_matrix[idx][3] = round(float(_row[3])/float(sum_eig),3)
      nor_matrix[idx][4] = round(float(_row[4]) / float(sum_dgr), 3)
      #nor_matrix[idx][5] = round(float(_row[5]) / float(sum_katz), 3)
    self._perf_mx = nor_matrix
    return nor_matrix

  def compute_nlog(self, value):
    e = 2.718
    nvalue = 0 if value == 0 else value * math.log(value, e)
    return nvalue

  def compute_entropy_measure_matrix(self):
    perf_matrix = self.compute_performance_indices_matrix()
    k = -1/self.compute_nlog(len(self.vertices))
    sum_matrix = [0 for _ in range(5)]
    ent_mx_stp1 = [[0, 0, 0, 0, 0] for i in range(len(self.network))]
    for idx, _row in enumerate(perf_matrix):
      crb_et  = self.compute_nlog(_row[0])
      ent_mx_stp1[idx][0] = crb_et
      sum_matrix[0] += crb_et
      bwd_et = self.compute_nlog(_row[1])
      ent_mx_stp1[idx][1] = bwd_et
      sum_matrix[1] += bwd_et
      bc_et = self.compute_nlog(_row[2])
      ent_mx_stp1[idx][2] = bc_et
      sum_matrix[2] += bc_et
      eig_et = self.compute_nlog(_row[3])
      ent_mx_stp1[idx][3] = eig_et
      sum_matrix[3] += eig_et
      n_degree = self.compute_nlog(_row[4])
      ent_mx_stp1[idx][4] = n_degree
      sum_matrix[4] += eig_et
      # n_katz = self.compute_nlog(_row[5])
      # ent_mx_stp1[idx][5] = n_katz
      # sum_matrix[5] += eig_et
    entp_measure_mx = [1 - (k * vl) for vl in sum_matrix]
    entp_measure = sum(entp_measure_mx)
    weight_mx = [evl/entp_measure for evl in entp_measure_mx]
    #print(f"\nNORD Weight_mx sum_crb, sum_bdwth, sum_bc, sum_eig, sum_dgr, sum_katz  {weight_mx}" )   #LIST OF WEIGHTS
    logging.info(f"\t\t NORD The Weight_mx is sum_crb, sum_bdwth, sum_bc, sum_eig, sum_dgr {weight_mx}%")
# TOPSIS will start here
    #get weighted normalized matirx
    weighted_nor_mx = [[0, 0, 0, 0, 0] for i in range(len(self.network))]
    for i in range(len(self._perf_mx)):
      for k in range(len(weight_mx)):
        weighted_nor_mx[i][k] = self._perf_mx[i][k] * weight_mx[k] # NORMALIZED MATRIX * wEIGHTS

    # get max and min of column matrix
    max_list = list(map(max, zip(*weighted_nor_mx)))
    min_list = list(map(min, zip(*weighted_nor_mx)))

    ## max_list - weighted_nor_mx
    max_weight_nor_mx = [[0, 0, 0, 0, 0] for i in range(len(self.network))]
    min_weight_nor_mx = [[0, 0, 0, 0, 0] for i in range(len(self.network))]
    for i in range(len(weighted_nor_mx)):
      for k in range(len(max_list)):
        max_weight_nor_mx[i][k] = max_list[k] - weighted_nor_mx[i][k]
        min_weight_nor_mx[i][k] = min_list[k] - weighted_nor_mx[i][k]

    s_plus_mx = [[] for i in range(len(self.network))] #
    for _idx in range(len(max_weight_nor_mx)):
      s_plus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                      max_weight_nor_mx[_idx]))]
    s_minus_mx = [[] for i in range(len(self.network))]
    for _idx in range(len(min_weight_nor_mx)):
      s_minus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
                                       min_weight_nor_mx[_idx]))]
    ## s_plus_mx + s_minus_mx
    s_plus_plus = [[0] for i in range(1, len(self.network)+1)]
    for i in range(len(s_plus_mx)):
      for k in range(len(s_plus_plus[i])):
        s_plus_plus[i][k] = s_plus_mx[i][k] + s_minus_mx[i][k]
    s_plus_plus_dict = {}
    for idx, k in enumerate(self.vertices): #
      s_plus_plus_dict[k] = s_plus_plus[idx][0]

    ## get rank values
    rank_dict = {}
    for idx, k in enumerate(self.vertices):
      # rank_dict[k] = s_minus_mx[idx][0]/s_plus_plus[idx][0]
      rank_dict[k] = 0 if (s_minus_mx[idx][0] == 0 and s_plus_plus[idx][0] ==
                           0) else s_minus_mx[idx][0]/s_plus_plus[idx][0]
    ## generate rank for nodes
    node_rank = {key: rank for rank, key in enumerate(sorted(rank_dict,
                                                             key=rank_dict.get, reverse=True), 1)}
    # print ('+' * 100 + '\n')
    # print (f'Rank generation value for nodes \n\t{rank_dict}\n')

    # print (f'Rank generated for nodes (Node\tRank) \n\t{node_rank}\n')

    logging.info(f'Rank generation value for nodes \n\t{rank_dict}')
    logging.info(f'Rank generated for nodes (Node\tRank) \n\t{node_rank}')
    return node_rank