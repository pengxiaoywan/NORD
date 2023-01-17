
import math
import logging
log = logging.getLogger(__name__)


class BetweennessCentrality(object):
  def __init__(self, network):
    self.network = network
    self.vertices = network.keys()

  def find_all_paths(self, start, end, path=[]):
    path = path + [start]
    if start == end:
      return [path]
    if start not in self.vertices:
      return []
    paths = []
    for node in self.network[start]:
      if node not in path:
        newpaths = self.find_all_paths(node, end, path)
        for newpath in newpaths:
          paths.append(newpath)
    return paths

  @staticmethod
  def get_shortest_path_dist(paths):
    paths.sort(key=len)
    short_path = paths[0]
    log.info( 'all found paths: %s' % paths)
    return [_path for _path in paths if len(_path) == len(short_path)]

  def betweenness_centrality_node(self, node):
    node_pair_list = []
    bc_sum_node = 0
    for start_node in self.vertices:
      for end_node in self.vertices:
        node_pair = [start_node, end_node]
        node_pair.sort()
        if (start_node != end_node) and (start_node != node) and \
            (end_node != node) and (node_pair not in node_pair_list):
          all_shortest_paths = self.find_all_paths(start_node, end_node, path=[])
          shortest_paths = self.get_shortest_path_dist(all_shortest_paths)
          path_count, bc_node_in_path = 0, 0
          for sp_path in shortest_paths:
            if node in sp_path:
              bc_node_in_path += 1
            path_count += 1
          if path_count != 0:
            bc_node_pair = float(bc_node_in_path) / float(path_count) # Shortest path via Target node/ total shortest path
            bc_sum_node += bc_node_pair
            log.info( "node pair: %s" % node_pair)
            log.info( 'shortest paths: %s' % shortest_paths)
            log.info ('No. of path with min length %s, node found in path %s'% (
              path_count, bc_node_in_path))
            log.info( 'BC of node pair %s is %s' % (node_pair,bc_node_pair))
            log.info( '-'*50)
          node_pair_list.append(node_pair)
    log.info ('BC of node %s is %s' % (node, bc_sum_node))
    log.info ('+' * 50 +'\n')
    return bc_sum_node

  def betweenness_centrality(self):
    bwt_cnt = {}
    for _node in self.network.keys():
      bwt_cnt[_node] = self.betweenness_centrality_node(_node)
    log.info ('Betweenness centrality of all nodes: %s' % bwt_cnt)
    return self.normalised_betweenness_centrality(bwt_cnt)

  def normalised_betweenness_centrality(self, centrality_dict):
    normalised_bt_cnt = {}
    total_n_value = math.sqrt(sum(value ** 2 for value in centrality_dict.values()))
    for elem in centrality_dict:
      normalised_bt_cnt[elem] = float(centrality_dict[elem])/float(
        total_n_value) if total_n_value != 0 else 0
    _normalised_bt_cnt = {ky: round(vl, 3) for ky, vl in
                          normalised_bt_cnt.items()}
    log.info ('Normalised Betweenness centrality : %s' % _normalised_bt_cnt)
    return _normalised_bt_cnt