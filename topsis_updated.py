from turtle import right
# This one modified BFA_P
from topsis_helper_new import get_ranks #without katz
#from topsis_helper  import get_ranks  #with katz
import helper
import sys
import copy
from datetime import datetime, date
import logging
import math
from entropy import WeightMatrix
import config
from network_attributes import NetworkAttribute
from collections import OrderedDict
import networkx as nx

log=logging
FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(filename=r'topsis.log',
                    format=FORMAT,
                    filemode="w",
                    level=logging.DEBUG,
                    datefmt = '%Y-%m-%d %H:%M:%S %p')
class temp_map:
    def __init__(self, vne_list,req_no, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        self.node_cost += sum(vne_list[req_no].node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = dict()

def node_map(substrate, virtual, req_no):
    map = [0 for x in range(virtual.nodes)]
    sorder = get_ranks(substrate) # Non increasing
    #log.info(f"Substrate rank {sorder}")

    sn = dict()
    for i in range(substrate.nodes):
        ls = []
        for nd in substrate.neighbours[i]:
            ls.append(int(nd))
        sn[i] = ls
    
    sn_link_bw = {}
    _node_obj = NetworkAttribute(sn, crb=substrate.node_weights, link_bandwidth=sn_link_bw)
    sn_node_bw = _node_obj.normalized_node_bandwidth(substrate)
    sn_node_crb = _node_obj.normalized_crb(substrate)
    sn_crb = _node_obj.get_network_crb()
    sn_link_bw = _node_obj.get_link_bandwidth()
    
    sn_node_degree=_node_obj.normalized_node_degree()
    
    sn_btw_cnt = nx.betweenness_centrality(nx.DiGraph(sn))      #ADDED - inbuilt function for betweeness centrality
    sn_eigned_vct = nx.eigenvector_centrality(nx.DiGraph(sn), max_iter = 10000)   #ADDED - inbuilt function for eigenvector centrality
  
    sn_rank = WeightMatrix(sn, sn_node_crb, sn_node_bw, sn_btw_cnt,
                             sn_eigned_vct,sn_node_degree).compute_entropy_measure_matrix()


    # log.info(f"Sn rank {sn_rank.keys()}")                         
    #print(f"Ranks for substrate {sorder}")


    vorder = get_ranks(virtual) 
    # log.info(f"VNR rank {vorder}")
    #print(f"Ranks for vne {vorder}")

    _vne = dict()
    for i in range(virtual.nodes):
        ls = []
        for nd in virtual.neighbours[i]:
            ls.append(int(nd))
        _vne[i] = ls

    vne_node_attrib = NetworkAttribute(_vne, virtual=True)
    node_norm_bw = vne_node_attrib.normalized_node_bandwidth(virtual)
    node_norm_crb = vne_node_attrib.normalized_crb(virtual)
    node_bw = vne_node_attrib.get_network_bandwidth()
    node_crb = vne_node_attrib.get_network_crb()
    link_bw = vne_node_attrib.get_link_bandwidth()
    node_degree = vne_node_attrib.normalized_node_degree()
    _vnode = [_vne, node_bw, node_crb, node_norm_bw,
                            node_norm_crb, link_bw, node_degree]
    btw_cnt = nx.betweenness_centrality(nx.DiGraph(_vnode[0]))
    eigned_vct = nx.eigenvector_centrality(nx.DiGraph(_vnode[0]), max_iter = 1000)
    #WeightMatrix=
    node_rank = WeightMatrix(_vnode[0], _vnode[4], _vnode[3], btw_cnt,
                             eigned_vct, _vnode[6]).compute_entropy_measure_matrix() # Compute Weight of the attributes

    # log.info(f"Vn rank {node_rank.keys()}")



    sorder = list(sn_rank.keys())
    vorder = list(node_rank.keys())
    assigned_nodes = set()
    for vnode in vorder:
        for snode in sorder:
            if substrate.node_weights[snode] >= virtual.node_weights[vnode] and snode not in assigned_nodes:
                map[vnode] = snode
                substrate.node_weights[snode] -= virtual.node_weights[vnode]
                assigned_nodes.add(snode)
                break
            if snode == sorder[-1]:
                return None
    return map

# Find all possible paths for Source to destination
def find_all_paths(network, start, end, path=[]):
  path = path + [start]
  if start == end:
    return [path]
  paths = []
  for node in network.neighbours[int(start)]:
    node = int(node)
    if node not in path:
      newpaths = find_all_paths(network, node, end, path)
      for newpath in newpaths:
        paths.append(newpath)
  return paths


def map_virtual_link_on_substrate(paths, vne_bw, sn_link_bw):
  paths.sort(key=len)
  link_nodes = []
  for _path in paths:
    node_path = generate_link_paths(_path)
    for link in node_path:
      if vne_bw <= sn_link_bw[(str(link[0]),str(link[1]))]:
        link_nodes.append(link)
        sn_link_bw[(str(link[0]),str(link[1]))] -= vne_bw #
        sn_link_bw[(str(link[1]),str(link[0]))] -= vne_bw #
    if link_nodes and (len(link_nodes) == len(node_path)):
      return OrderedDict(link_nodes), sn_link_bw
  return {}, sn_link_bw

# To get path from Source to destination
def generate_link_paths(path_list):
  node_path = []
  prev_n = path_list[0]
  for i in range(len(path_list) - 1):
    next_n = path_list[i + 1]
    node_path.append((prev_n, next_n))
    prev_n = next_n
  return node_path

path1_cnt=0
path2_cnt=0
def edge_map(substrate, virtual, req_no, req_map, vne_list):
    substrate_copy = copy.deepcopy(substrate)
    substrate_copy2 = copy.deepcopy(substrate)
    global path1_cnt
    global path2_cnt
    pc = True
    pc2 = True
    for edge in virtual.edges:
        if int(edge[0]) < int(edge[1]):
            weight = virtual.edge_weights[edge]
            left_node = req_map.node_map[int(edge[0])]
            right_node = req_map.node_map[int(edge[1])]
            
            all_shortest_paths = find_all_paths(copy.deepcopy(substrate), left_node, right_node,
                                        path=[])
            shortest_paths, sn_bandw = map_virtual_link_on_substrate(all_shortest_paths,
                                            weight,substrate_copy2.edge_weights)
            shortPath_ls = []
            cnt = 0
            for ed in shortest_paths:
                if cnt==0:
                    shortPath_ls.append(str(ed))
                shortPath_ls.append(str(shortest_paths[ed]))
                cnt += 1

            path = substrate_copy.findShortestPath(str(left_node), str(right_node), weight) # modified bfs

            path2 = shortPath_ls
            
            # print(path)
            # print(path2)
            # print()
            if(path2 == []):
                pc2 = False
            if(path == []):
                pc = False
            if path != []:
                req_map.edge_map[req_no, edge] = path
                for j in range(1, len(path)):
                    substrate_copy.edge_weights[(path[j - 1], path[j])] -= weight
                    substrate_copy.edge_weights[(path[j], path[j - 1])] -= weight
                    req_map.edge_cost += weight
            else:
                return False
    
    if(pc2 == True):
        path2_cnt += 1
    if(pc == True):
        path1_cnt += 1
    sub_wt = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x], reverse=True) # ascending order
    for node in sorder:
        sub_wt.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tSubstrate node before mapping VNR-{req_no} is {sub_wt}")
    sub_wt = []
    for edge in substrate.edges:
        sub_wt.append((edge, substrate.edge_weights[edge]))
    logging.info(f"\t\tSubstrate edge before mapping VNR-{req_no} is {sub_wt}")
    logging.info(f"\t\tNode map of VNR-{req_no} is {req_map.node_map}")
    logging.info(f"\t\tEdge map of VNR-{req_no} is {req_map.edge_map}")
    for edge, path in req_map.edge_map.items():
        edge = edge[1]
        for i in range(1,len(path)):
            substrate.edge_weights[(path[i - 1], path[i])] -= virtual.edge_weights[edge]
            substrate.edge_weights[(path[i], path[i-1])] -= virtual.edge_weights[edge]
    for node in range(vne_list[req_no].nodes):
        substrate.node_weights[req_map.node_map[node]] -= virtual.node_weights[node]
    sub_wt = []
    sorder = sorted([a for a in range(substrate.nodes)], key = lambda x: substrate.node_weights[x], reverse=True) # ascending order
    for node in sorder:
        sub_wt.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tSubstrate after mapping VNR-{req_no} is {sub_wt}")
    sub_wt = []
    for edge in substrate.edges:
        sub_wt.append((edge, substrate.edge_weights[edge]))
    logging.info(f"\t\tSubstrate edge after mapping VNR-{req_no} is {sub_wt}")
    return True

def findAvgPathLength(vnr):
    cnt=0
    for node1 in range(vnr.nodes):
        for node2 in range(vnr.nodes):
            if(node1 != node2):
                path = vnr.findShortestPath(str(node1), str(node2), 0)
                cnt += len(path)-1
    total_nodes = vnr.nodes
    cnt /= (total_nodes)*(total_nodes-1)
    return cnt
   
def main():
    print(f"\t\t{datetime.now().time()}\tTopsis Started")
    # substrate, vne_list = helper.read_pickle()
    substrate, vne_list = copy.deepcopy(config.substrate), copy.deepcopy(config.vne_list)
    copy_sub = copy.deepcopy(substrate)
    logging.basicConfig(filename="topsis.log",filemode="w", level=logging.INFO)

    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    logging.info(f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    temp.sort(key=lambda y: y[1])
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge,substrate.edge_weights[edge]))
    temp.sort(key=lambda y: y[1])
    logging.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK")

    total_vnr_nodes = 0
    total_vnr_links = 0
    logging.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    for vnr in range(len(vne_list)):
        logging.info(f"\t\tTotal number of nodes and edges in VNR-{vnr} is : {vne_list[vnr].nodes} and {len(vne_list[vnr].edges)}")
        temp = []
        total_vnr_nodes += vne_list[vnr].nodes
        for node in range(vne_list[vnr].nodes):
            temp.append((node, vne_list[vnr].node_weights[node]))
        logging.info(f"\t\tNodes of the VNR-{vnr} with weight are : {temp}")
        temp = []
        total_vnr_links += len(vne_list[vnr].edges)
        for edge in vne_list[vnr].edges:
            temp.append((edge, vne_list[vnr].edge_weights[edge]))
        if vnr == len(vne_list)-1:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}\n\n")
        else:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}")        

    start_time = datetime.now().time()
    accepted = 0
    revenue = 0
    path_cnt=0
    avg_path_length = 0
    avg_path_length_modified = 0
    curr_map = dict() # only contains the requests which are successfully mapped
    pre_resource_edgecost = sum(substrate.edge_weights.values())//2 # total available bandwidth of the physical network
    pre_resource_nodecost = sum(substrate.node_weights.values()) # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost
    revenue_list = [-1 for _ in range(len(vne_list))]
    for req in range(len(vne_list)):
        revenue_list[req] = sum(vne_list[req].node_weights.values()) + sum(vne_list[req].edge_weights.values())//2
    req_order = sorted(list(range(len(vne_list))), key=lambda x:revenue_list[x]) # Asceding order of revenue
    #req_order = sorted(list(range(len(vne_list))), key=lambda x:revenue_list[x], reverse = True) # Descending order of revenue
    for req_no in req_order:
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is  None:
            #print(f"Node mapping not possible for req no {req_no}")
            logging.warning(f"\tNode mapping not possible for req no {req_no}\n")
            continue
        req_map = temp_map(vne_list, req_no, req_map)
        if not edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list):
            #print(f"Edge mapping not possible for req no {req_no}")
            logging.warning(f"\tEdge mapping not possible for req no {req_no}\n")
            continue
        accepted += 1
        path_count_modified = 0
        for ed in req_map.edge_map:
            path_cnt += len(req_map.edge_map[ed])
            path_count_modified += (len(req_map.edge_map[ed]) - 1)
        
        avg_path_length_modified += (path_count_modified / (len(vne_list[req_no].edges)//2))
        avg_path_length += findAvgPathLength(vne_list[req_no])
        req_map.total_cost = req_map.node_cost + req_map.edge_cost
        #print(f"Mapping for request {req_no} is done successfully!! {req_map.node_map} with total cost {req_map.total_cost}")
        logging.info(f"\t\tMapping for request {req_no} is done successfully!! {req_map.node_map} with revenue {sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2} and total cost {req_map.total_cost}\n")
        curr_map[req_no] = req_map
        revenue += sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2

    # print(path1_cnt)
    # print(path2_cnt)
    ed_cost  = 0
    no_cost = 0
    for request in curr_map.values():
        ed_cost += request.edge_cost # total bandwidth for all the mapped requests
        no_cost += request.node_cost # total crb for all the mapped requests
    tot_cost = ed_cost + no_cost

    post_resource_edgecost =0
    post_resource_nodecost=0
    utilized_nodes=0
    utilized_links=0
    average_node_utilization = 0
    average_edge_utilization = 0
    for edge in substrate.edge_weights:
        post_resource_edgecost += substrate.edge_weights[edge]
        if substrate.edge_weights[edge]!=copy_sub.edge_weights[edge]:
            utilized_links += 1
            average_edge_utilization += ((copy_sub.edge_weights[edge]-substrate.edge_weights[edge])/copy_sub.edge_weights[edge])
            logging.info(f"The edge utilization of substrate edge {edge} is {((copy_sub.edge_weights[edge]-substrate.edge_weights[edge])/copy_sub.edge_weights[edge])*100:0.4f}")
    post_resource_edgecost //= 2
    if utilized_links != 0:
        average_edge_utilization = average_edge_utilization / 2
        average_edge_utilization /= (utilized_links//2)
    for node in substrate.node_weights:
        post_resource_nodecost += substrate.node_weights[node]
        if substrate.node_weights[node] != copy_sub.node_weights[node]:
            utilized_nodes += 1
            average_node_utilization += ((copy_sub.node_weights[node]-substrate.node_weights[node])/copy_sub.node_weights[node])
            logging.info(f"The node utilization of the substrate node:{node} is {((copy_sub.node_weights[node]-substrate.node_weights[node])/copy_sub.node_weights[node])*100:0.4f}")
    if utilized_nodes!=0:
        average_node_utilization /= utilized_nodes

    if(accepted != 0):
        avg_path_length /= accepted
        avg_path_length_modified /= accepted
    post_resource = post_resource_edgecost + post_resource_nodecost
    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    
    #print(f"\n\nThe revenue is {revenue} and total cost is {tot_cost}")
    #print(f"Total number of requests embedded is {accepted}")
    #print(f"Embedding ratio is {accepted/len(vne_list)}")
    #print(f"Availabe substrate resources before mapping is {pre_resource}")
    #print(f"Consumed substrate resources after mapping is {pre_resource - post_resource}")
    #print(f"Average link utilization {ed_cost/pre_resource_edgecost}")
    #print(f"Average node utilization {no_cost/pre_resource_nodecost}")
    #print(f"Average execution time {duration/len(vne_list)}")

    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK AFTER MAPPING VNRs")
    logging.info(f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    temp.sort(key=lambda y: y[1])
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge,substrate.edge_weights[edge]))
    temp.sort(key=lambda y: y[1])
    logging.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n")   
    
    logging.info(f"\t\tThe revenue is {revenue} and total cost is {tot_cost}")
    if tot_cost == 0:
        logging.error(f"\t\tCouldn't embedd any request")
        output_dict = {
            "revenue": -1,
            "total_cost": -1,
            "accepted": -1,
            "total_request": -1,
            "pre_resource": -1,
            "post_resource": -1,
            "avg_bw": -1,
            "avg_crb": -1,
            "avg_link": -1,
            "avg_node": -1,
            "avg_path": -1,
            "avg_exec": (duration),
            "total_nodes": total_vnr_nodes,
            "total_links": total_vnr_links//2,
        }
        #print(f"\t\t{datetime.now().time()}\tVikor completed\n")
        return output_dict

    logging.info(f"\t\tThe revenue to cost ratio is {(revenue/tot_cost)*100:.4f}%")
    logging.info(f"\t\tTotal number of requests embedded is {accepted} out of {len(vne_list)}")
    logging.info(f"\t\tEmbedding ratio is {(accepted/len(vne_list))*100:.4f}%\n")
    logging.info(f"\t\tTotal {utilized_nodes} nodes are utilized out of {len(substrate.node_weights)}")
    logging.info(f"\t\tTotal {utilized_links//2} links are utilized out of {len(substrate.edge_weights)//2}")
    # logging.info(f"\t\tAverage node utilization is {(utilized_nodes/len(substrate.node_weights))*100:0.4f}")
    # logging.info(f"\t\tAverage link utilization is {(utilized_links/len(substrate.edge_weights))*100:0.4f}\n")
    logging.info(f"\t\tAverage node CRB utilization is {average_node_utilization*100:0.4f}")
    logging.info(f"\t\tAverage link BW utilization is {average_edge_utilization*100:0.4f}\n")
    logging.info(f"\t\tAvailabe substrate before embedding CRB: {pre_resource_nodecost} BW: {pre_resource_edgecost} total: {pre_resource}")
    logging.info(f"\t\tAvailabe substrate after embedding CRB: {post_resource_nodecost} BW: {post_resource_edgecost} total: {post_resource}")
    logging.info(f"\t\tConsumed substrate CRB: {pre_resource_nodecost-post_resource_nodecost} BW: {pre_resource_edgecost-post_resource_edgecost} total: {pre_resource - post_resource}\n")
    # logging.info(f"\t\tAverage Path length is {avg_path_length:.4f}\n")
    logging.info(f"\t\tAverage Path length is {avg_path_length_modified:.4f}\n")
    # logging.info(f"\t\tAverage BW utilization {(ed_cost/pre_resource_edgecost)*100:.4f}%")
    # logging.info(f"\t\tAverage CRB utilization {(no_cost/pre_resource_nodecost)*100:.4f}%")
    logging.info(f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n")
    # logging.shutdown()
    output_dict = {
        "revenue": revenue,
        "total_cost" : tot_cost,
        "accepted" : accepted,
        "total_request": len(vne_list),
        "pre_resource": pre_resource,
        "post_resource": post_resource,
        "avg_bw": (average_edge_utilization)*100,
        "avg_crb": (average_node_utilization)*100,
        "avg_link": ((utilized_links/len(substrate.edge_weights))/2)*100,
        "No_of_Links_used": (utilized_links)//2,
        "avg_node": (utilized_nodes/len(substrate.node_weights))*100,
        "No_of_Nodes_used": (utilized_nodes),
        "avg_path": avg_path_length_modified,
        "avg_exec": (duration),
        "total_nodes": total_vnr_nodes,
        "total_links": total_vnr_links//2,
    }
    print(f"\t\t{datetime.now().time()}\tTopsis completed\n")
    return output_dict

if __name__ == '__main__':
    '''
    The output can be different for same input file also.
    Because there can be multiple shortest paths from source to destination.
    '''
    # helper.setup_logger('log1','vikor.log')
    main()