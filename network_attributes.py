import math
import random

class NetworkAttribute(object):

  def __init__(self, network, virtual=False, **kwargs):
    self.virtual = virtual
    self.network = network
    self.vertices = network.keys()
    self.network_crb = kwargs.get('crb',{})
    self.network_bdwth = {}
    self.network_revenue = {}
    self.link_bandwidth = kwargs.get('link_bandwidth',{})
    self.crb_unit_cost = 1
    self.bwd_unit_cost = 1
    self.node_degree = {}

  def generate_crb(self, original_net):
    if self.network_crb:
      return self.network_crb
    network_crb = dict()
    for i in self.network:
      network_crb[i] = original_net.node_weights[i]
    #print ("Initial Node CRB %s" % network_crb)
    self.network_crb = network_crb
    return network_crb

  def get_network_crb(self):
    return self.network_crb

  def get_network_bandwidth(self):
    return self.network_bdwth

  def get_link_bandwidth(self):
    return self.link_bandwidth

  def get_network_revenue(self):
    return self.network_revenue

  def generate_node_degree(self):
    for i in self.network:
      self.node_degree[i] = len(self.network[i])
    return self.node_degree

  def get_node_degree(self):
    return self.node_degree

  def generate_node_bandwidth(self, original_net):
    node_bandwidth = dict()
    ## calculate link bandwidth
    if not self.link_bandwidth:
      for i in self.network:
        for j in self.network[i]:
          if (j, i) in self.link_bandwidth:
            self.link_bandwidth[(i, j)] = self.link_bandwidth[(j, i)]
          else:
            self.link_bandwidth[(i, j)] = original_net.edge_weights[(str(i), str(j))]
    # calulate bandwidth strength of individual node
    for _node in self.network:
      node_wt = 0
      for _link in self.network[_node]:
        node_wt += self.link_bandwidth[(_node, _link)]
      node_bandwidth[_node] = node_wt
    #print ("Initial Node Bandwidth %s" % node_bandwidth)
    self.network_bdwth = node_bandwidth
    return node_bandwidth

  def normalized_crb(self, original_net):
    nt_crb = self.generate_crb(original_net)
    total_n_value = math.sqrt(sum(value ** 2 for value in nt_crb.values()))
    normalised_crb = {}
    for elem in nt_crb:
      normalised_crb[elem] = float(nt_crb[elem])/float(total_n_value)
    _normalised_crb = {ky:round(vl, 2) for ky, vl in normalised_crb.items()}
    #print( 'Normalised CRB : %s' % _normalised_crb)
    return _normalised_crb

  def normalized_node_bandwidth(self, original_net):
    nt_bwdth = self.generate_node_bandwidth(original_net)
    total_n_value = math.sqrt(sum(value ** 2 for value in nt_bwdth.values()))
    normalised_bwdth = {}
    for elem in nt_bwdth:
      normalised_bwdth[elem] = float(nt_bwdth[elem])/float(total_n_value)
    _normalised_bwdth = {ky:round(vl, 2) for ky, vl in normalised_bwdth.items()}
    #print( 'Normalised Node Bandwidth : %s' % _normalised_bwdth)
    return _normalised_bwdth

  def normalized_node_degree(self):
    nt_degree = self.generate_node_degree()
    total_n_value = math.sqrt(sum(value ** 2 for value in nt_degree.values()))
    normalised_degree = {}
    for elem in nt_degree:
      normalised_degree[elem] = float(nt_degree[elem]) / float(total_n_value)
    _normalised_degree = {ky: round(vl, 2) for ky, vl in
                       normalised_degree.items()}
    #print ('Normalised Degree : %s' % _normalised_degree)
    return _normalised_degree