import numpy as np
import sys
import logging
import random
import copy
import config
import networkx as nx
import math
from datetime import datetime, date


def main():

    substrate, vne_list = copy.deepcopy(config.substrate), copy.deepcopy(config.vne_list)
    output = {"substrate": substrate, "vne_list": vne_list}

    # ---------------------------------Need to be printed (Start)--------------------------
    # print("Substrate ")
    # print("--------------------------------------------------------------")
    # # print("Nodes: ", vne.nodes)
    # print("Nodes & their Weights: ", substrate.node_weights)
    # # print("Edges: ", vne.edges)
    # print("Edge & their Weights: ", substrate.edge_weights)
    # print("Adj List: ", substrate.neighbours)
    # print()
    # print()
    # print()
    # print()
    # ---------------------------------Need to be printed (End)--------------------------

    logging.basicConfig(filename="DAA.log", filemode="w", level=logging.INFO)
    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs for DAA)")
    logging.info(
        f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} ")

    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")

    temp = []
    for edge in substrate.edges:
        temp.append((edge, substrate.edge_weights[edge]))
    logging.info(f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK")


    logging.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    total_vnr_nodes = 0
    total_vnr_links = 0

    for i in range(len(vne_list)):
        logging.info(
            f"\t\tTotal number of nodes and edges in VNR-{i} is : {vne_list[i].nodes} and {len(vne_list[i].edges)}")
        vne = vne_list[i]
        temp = []
        total_vnr_nodes += vne_list[i].nodes
        for node in range(vne_list[i].nodes):
            temp.append((node, vne_list[i].node_weights[node]))
        logging.info(f"\t\tNodes of the VNR-{i} with weight are : {temp}")

        temp = []
        total_vnr_links += len(vne_list[i].edges)
        for edge in vne_list[i].edges:
            temp.append((edge, vne_list[i].edge_weights[edge]))
        if i == len(vne_list) - 1:
            logging.info(f"\t\tEdges of the VNR-{i} with weight are : {temp}\n\n")
        else:
            logging.info(f"\t\tEdges of the VNR-{i} with weight are : {temp}")

        logging.info(f"Request - {i + 1}")
        logging.info(f"VNE Request")
        logging.info(f"Nodes & their Weights: {vne.node_weights}")
        logging.info(f"Edge & their Weights: {vne.edge_weights}")
        logging.info(f"Adj List: ", vne.neighbours)
        logging.info(f"\t\t\t\t\t")
        # ---------------------------------Need to be printed (Start)--------------------------
        # print("Request ", i + 1)
        # print("--------------------------------------------------------------")
        # print("VNE Request")
        # # print("Nodes: ", vne.nodes)
        # print("Nodes & their Weights: ", vne.node_weights)
        # # print("Edges: ", vne.edges)
        # print("Edge & their Weights: ", vne.edge_weights)
        # print("Adj List: ", vne.neighbours)
        # print()
        # ---------------------------------Need to be printed (End)--------------------------

    # Calculate the sum of all nodes weight of graph
    def nodes_sum(graph):
        return sum(graph.node_weights.values())

    # Calculate the sum of all edges weight of graph
    def edges_sum(graph):
        return sum(graph.edge_weights.values())//2

    def compute_strength(graph):
        strg = [0] * graph.nodes
        for src, weight in graph.node_weights.items():
            sum_edge_wght = 0
            for dst in graph.neighbours[src]:
                sum_edge_wght += graph.edge_weights[(str(src), dst)]
            strg[src] = sum_edge_wght
        arr_np = np.array(strg)
        return arr_np

    def compute_rank_weight_strength(graph):
        strg = dict()
        for src, weight in graph.node_weights.items():
            sum_edge_wght = 0
            for dst in graph.neighbours[src]:
                sum_edge_wght += graph.edge_weights[(str(src), dst)]
            strg[src] = sum_edge_wght*weight
        return strg

    def compute_ratio(graph1,graph2):
        calc_ratio = dict()
        for src,weight in graph1.node_weights.items():
            util = (graph1.node_weights[src]-graph2.node_weights[src])/graph1.node_weights[src]
            calc_ratio[src]=util
        return calc_ratio

    def compute_energy(graph1,graph2):
        calc_energy = dict()
        for src,weight in graph1.node_weights.items():
            util = (graph1.node_weights[src]-graph2.node_weights[src])/graph1.node_weights[src]
            # energy = graph1.node_idle_energy[src]+(graph1.node_busy_energy[src]-graph1.node_idle_energy[src])*util
            calc_energy[src]=1
        return calc_energy

    def compute_cnrm(H,Ratio,PN,graph):
        CNRM = dict()
        for src,weight in graph.node_weights.items():
            CNRM[src]=(H[src]*(1-Ratio[src]))/PN[src]
        return CNRM

    def calc_energy_per_node(curr_substrate,s_nd_id,vne,v_nd_id,substrate):
        util=(curr_substrate.node_weights[s_nd_id]-vne.node_weights[v_nd_id])/substrate.node_weights[s_nd_id]
        calc_energy=curr_substrate.node_idle_energy[s_nd_id]+(curr_substrate.node_busy_energy[s_nd_id]-curr_substrate.node_idle_energy[s_nd_id])*util
        return calc_energy

    def compute_bw(graph):
        G = nx.Graph()
        G.add_nodes_from(nx.path_graph(graph.nodes))
        for edge in graph.edges:
            G.add_edge(int(edge[0]), int(edge[1]), weight=graph.edge_weights[edge])
        centrality = nx.betweenness_centrality(G)
        centrality = np.array([centrality[i] for i in range(graph.nodes)])
        return centrality

    # def normalize_mat(data):
    #     data = data.astype(np.float32)
    #     col_sum = np.sum(data, axis=0)
    #     # print(col_sum)
    #     for i in range(len(data)):
    #         for j in range(len(data[0])):
    #             # print(data[i][j], end=" ")
    #             data[i][j] /= col_sum[j]
    #         # print()
    #     return data
    #
    # def convt_dict(graph):
    #     graph = graph.neighbours
    #     network = {}
    #     for key, value in graph.items():
    #         network[key] = [int(i) for i in value]
    #     return network
    #
    # def get_weights(data, number_of_nodes):
    #     data = data.astype(np.float32)
    #     for i in range(len(data)):
    #         for j in range(len(data[0])):
    #             # print(data[i][j], end=" ")
    #             if data[i][j]!=0:
    #                 data[i][j] *= np.log(data[i][j])
    #             else:
    #                 break
    #     # print(data)
    #     col_sum = np.sum(data, axis=0)
    #     # print(col_sum)
    #     neg_h = (-1) / np.log(number_of_nodes) #value of h
    #
    #     #col_sum_new is ej
    #     ej = col_sum * neg_h
    #     # print(col_sum_new)
    #
    #     #dj = 1 - ej = degree of diversification
    #     dj = 1 - ej
    #     # print(col_sum_new2)
    #     total_sum_col_sum = np.sum(dj)
    #     # print(total_sum_col_sum)
    #     wj = dj / (total_sum_col_sum)
    #     return wj
    #
    #
    # def topsis_ranking(graph_dict, graph, weight_mx, _perf_mx):
    #     # get weighted normalized matirx
    #     weighted_nor_mx = [[0, 0, 0, 0] for i in range(graph.nodes)]
    #     for i in range(len(_perf_mx)):
    #         for k in range(len(weight_mx)):
    #             weighted_nor_mx[i][k] = _perf_mx[i][k] * weight_mx[k]
    #
    #     # get max and min of column matrix
    #     max_list = list(map(max, zip(*weighted_nor_mx)))
    #     min_list = list(map(min, zip(*weighted_nor_mx)))
    #
    #     ## max_list - weighted_nor_mx
    #     max_weight_nor_mx = [[0, 0, 0, 0] for i in range(graph.nodes)]
    #     min_weight_nor_mx = [[0, 0, 0, 0] for i in range(graph.nodes)]
    #     for i in range(len(weighted_nor_mx)):
    #         for k in range(len(max_list)):
    #             max_weight_nor_mx[i][k] = max_list[k] - weighted_nor_mx[i][k]
    #             min_weight_nor_mx[i][k] = min_list[k] - weighted_nor_mx[i][k]
    #
    #     s_plus_mx = [[] for i in range(graph.nodes)]
    #     for _idx in range(len(max_weight_nor_mx)):
    #         s_plus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
    #                                          max_weight_nor_mx[_idx]))]
    #     s_minus_mx = [[] for i in range(graph.nodes)]
    #     for _idx in range(len(min_weight_nor_mx)):
    #         s_minus_mx[_idx] = [math.sqrt(sum(pow(value, 2) for value in
    #                                           min_weight_nor_mx[_idx]))]
    #     ## s_plus_mx + s_minus_mx
    #     s_plus_plus = [[0] for i in range(1, graph.nodes + 1)]
    #     for i in range(len(s_plus_mx)):
    #         for k in range(len(s_plus_plus[i])):
    #             s_plus_plus[i][k] = s_plus_mx[i][k] + s_minus_mx[i][k]
    #     s_plus_plus_dict = {}
    #     vertices = graph_dict.keys()
    #     for idx, k in enumerate(vertices):
    #         s_plus_plus_dict[k] = s_plus_plus[idx][0]
    #
    #     ## get rank values
    #     rank_dict = {}
    #     for idx, k in enumerate(vertices):
    #         # rank_dict[k] = s_minus_mx[idx][0]/s_plus_plus[idx][0]
    #         rank_dict[k] = 0 if (s_minus_mx[idx][0] == 0 and s_plus_plus[idx][0] ==
    #                              0) else s_minus_mx[idx][0] / (s_plus_plus[idx][0] + 1)
    #     return rank_dict
    #
    # def get_ranks(graph):  # For TOPSIS we are passing four parameter
    #     # 1: degree -
    #     # 2: strength(BW stregth of the node) -
    #     # 3: crb (of the node) -
    #     # 4: betweenness Centrality
    #     #------------------------------
    #
    #     degree = np.array([len(graph.neighbours[i]) for i in range(graph.nodes)])
    #     bw_centrality = compute_bw(graph)
    #     strength = compute_strength(graph)
    #     crb = np.array([graph.node_weights[i] for i in range(graph.nodes)])
    #
    #     data = np.column_stack((degree, strength, crb)) #transpose
    #     # print(data)
    #     # step-2
    #     data = normalize_mat(data)
    #     # step-3
    #     weight_mat = get_weights(data, graph.nodes)  # attribute weights - entropy calc
    #     # print("weights:",weight_mat)
    #     # step-4
    #     return topsis_ranking(convt_dict(graph), graph, weight_mat, data.tolist())
    #

    # **Highest Resource Requirement (HRR)**
    HRR = {}
    for ix in range(len(vne_list)):
        vne = vne_list[ix]
        nd_sum = nodes_sum(vne)
        bw_sum = edges_sum(vne)
        HRR[ix] = [nd_sum + bw_sum, nd_sum, bw_sum]

    # ---------------------------------Need to be printed (Start)--------------------------
    # print(HRR)
    # ---------------------------------Need to be printed (End)--------------------------

    # **Node & Edge Mapping**

    VNEmbed_nodes = [-1] * len(vne_list)
    VNEmbed_edges = [-1] * len(vne_list)
    VNE_parameters = [[]] * len(vne_list)
    VNE_avgPath_len = [0] * len(vne_list)
    substrate_details = [(-1, -1)] * (len(vne_list) + 1)

    temp_curr_state_sg = copy.deepcopy(substrate)
    curr_state_sg = copy.deepcopy(temp_curr_state_sg)

    nodeSum_temp = nodes_sum(substrate)
    edgeSum_temp = edges_sum(substrate)

    substrate_details[0] = (nodeSum_temp, edgeSum_temp)

    preResource = nodeSum_temp + edgeSum_temp

    # ---------------------------------Need to be printed (Start)--------------------------

    # print("Inital state of physical graph\n" + " Node sum: " + str(nodeSum_temp).rjust(10)
    #       + " Edge sum: " + str(edgeSum_temp).rjust(10)
    #       + " Pre_resource: " + str(preResource).rjust(10))

    # ---------------------------------Need to be printed (End)--------------------------

    logging.info(f"\t\tInital state of physical graph\n Node sum : {str(nodeSum_temp).rjust(10)} \t "
                 f"Edge sum : {str(edgeSum_temp).rjust(10)} \t Pre_resource: {str(preResource).rjust(10)}")

    # print("---------------------------------------------------------------------\n")

    accepted_req = 0
    start_time = datetime.now().time()
    print()
    logging.info(f"PUVNP start time : {datetime.now().time()}")
    print(f"\t\t{datetime.now().time()}\tPUVNP started\n")
    # calc_CRB = 0
    # calc_BW = 0
    set_CRB=set()
    set_BW=set()

    total_energy_consumed=0

    # sn_topsis_rank = get_ranks(substrate)
    # sn_topsis_rank = sorted(sn_topsis_rank.items(), key=lambda kv: kv[1])

    # Embedding Process Started !!!!!!!!!!!!!!!!!!

    for vne_id, hrr in sorted(HRR.items(), key=lambda kv: (kv[1]), reverse=False):
        vne = vne_list[vne_id]
        revenue_vne = hrr[0]
        nd_sum = hrr[1]
        ed_sum = hrr[2]
        logging.info(f"\t\t VNR {vne_id+1} Revenue is {revenue_vne}, node sum is {nd_sum} and edge sum is {ed_sum}")
        # ---------------------------------Need to be printed (Start)--------------------------
        # print("Revenue: ", revenue_vne, " node weights sum = ", nd_sum, " edge weights sum = ", ed_sum)
        # ---------------------------------Need to be printed (End)--------------------------
        sn_cost_node = 0
        sn_cost_edge = 0
        mappingVtoS = {}
        mappingStoV = {}
        all_link_path_len_cur_vne = []

        temp_curr_state_sg = copy.deepcopy(curr_state_sg)

        # Node Mapping Started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        flag = False
        # sorted_vne = sorted(HRR.items(), key = lambda kv:(kv[1]), reverse=True)
        # vne_weight_rank = sorted(vne.node_weights.items(), key=lambda kv: (kv[1]))
        # sn_topsis_rank = get_ranks(substrate)

        # ---------------------------------Need to be printed (Start)--------------------------
        # print("Weights of each node of substrate")
        # print(sn_topsis_rank)
        # ---------------------------------Need to be printed (End)--------------------------
        # vne_topsis_rank = get_ranks(vne)
        vne_rank = compute_rank_weight_strength(vne)
        # print(vne.node_weights)
        # print(vne.edge_weights)
        # print(vne_rank)
        # print()

        # sorting the Nodes for VNE Request as per weight Ranking
        vne_rank=sorted(vne_rank.items(), key=lambda kv: (kv[1]), reverse=True)

        logging.info(f"Rank of Nodes of VR {vne_id + 1}\n")
        count = 0
        for nd, wt in vne_rank:
            count += 1
            logging.info(f"{count} : {nd, wt}\n")

        # print(substrate.busy_energy[0])

        # Ranking calculation of substrate Node
        #----------------------------------------------------

        H = compute_rank_weight_strength(temp_curr_state_sg) # H is a dictionary with key,value
        Ratio = compute_ratio(substrate,temp_curr_state_sg)
        PN = compute_energy(substrate,temp_curr_state_sg)

        CNRM = compute_cnrm(H,Ratio,PN,substrate)

        CNRM = sorted(CNRM.items(), key=lambda kv: (kv[1]), reverse=False)
        #----------------------------------------------------

        count = 0
        for nd, wt in CNRM:
            count += 1
            logging.info(f"{count} : {nd, wt}\n")
        # print(CNRM)

        # print(vne_rank)
        energy_consumed_per_request=0
        for nd_id, weight_strength_rank in vne_rank:
            nd_cap = vne.node_weights[nd_id]
            node_busy_energy=vne.node_busy_energy[nd_id]
            # sorting the Nodes for Substrate Network as per Topsis Ranking Algorithm each time a new request is encountered !!
            for s_nd_id, CNRM_rank in CNRM:
                s_nd_cap = curr_state_sg.node_weights[s_nd_id]
                # comparing Capacity of VNE and Substrate
                if nd_cap <= s_nd_cap and mappingStoV.get(str(s_nd_id)) == None:
                    mappingVtoS[str(nd_id)] = str(s_nd_id)
                    mappingStoV[str(s_nd_id)] = str(nd_id)
                    # calc_CRB+=(nd_cap/s_nd_cap)
                    set_CRB.add(s_nd_id)
                    curr_state_sg.node_weights[s_nd_id] -= nd_cap
                    sn_cost_node += nd_cap
                    # energy_consumed_per_request+=calc_energy_per_node(curr_state_sg,s_nd_id,vne,nd_id,substrate)
                    break

            if mappingVtoS.get(str(nd_id)) == None:
                flag = True
                curr_state_sg = temp_curr_state_sg
                energy_consumed_per_request=0
                logging.info(f"Unable to embed all nodes for VNRequest_ {vne_id+1} \t VNRequest Discarded")
                # ---------------------------------Need to be printed (Start)--------------------------
                # print("Unable to embed all nodes for VNRequest_", vne_id + 1, " VNRequest Discarded")
                # ---------------------------------Need to be printed (End)--------------------------
                VNE_parameters[vne_id - 1] = [0, 0, 0]
                break

        if flag:
            continue

        if len(mappingVtoS) == vne.nodes:
            logging.info(f"Node Mapping for VNRequest_ {vne_id + 1} is completed, Waiting for Link Mapping")
            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Node Mapping for VNRequest_", vne_id + 1, " is completed, Waiting for Link Mapping")
            # ---------------------------------Need to be printed (End)--------------------------
            # print(mappingVtoS)
            # print(mappingStoV)
        else:
            logging.info(f"Unable to embed all nodes for VNRequest_ {vne_id + 1} VNRequest Discarded")
            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Unable to embed all nodes for VNRequest_", vne_id + 1, " VNRequest Discarded")
            # ---------------------------------Need to be printed (End)--------------------------
            VNE_parameters[vne_id - 1] = [0, 0, 0]
            curr_state_sg = copy.deepcopy(temp_curr_state_sg)
            energy_consumed_per_request=0
            continue

        logging.info(f"Node Mapping from VR {vne_id+1} to Substrate Network :")
        logging.info(f"{mappingVtoS}\n")

        # ---------------------------------Need to be printed (Start)--------------------------
        # print(mappingVtoS)
        # ---------------------------------Need to be printed (End)--------------------------


        # Node Mapping Completed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Link Mapping Started !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


        link_map_VtoS = {}
        flag = False

        count=0

        for u, v in vne.edges:
            mapped_s_nd_u = mappingVtoS[u]
            mapped_s_nd_v = mappingVtoS[v]
            demand_uv = vne.edge_weights[(u, v)]
            # lst.append((u,v))
            # all_path_uv = curr_state_sg.printAllPaths(mapped_s_nd_u, mapped_s_nd_v, demand_uv)
            path_uv = curr_state_sg.findShortestPath(mapped_s_nd_u, mapped_s_nd_v, demand_uv)
            logging.info(f"Path from VR Node {u} to VR Node {v}")
            logging.info(f"{path_uv}")
            # print()
            # print(path_uv)
            # print("end")
            # all_path_uv.sort(key=len)
            x = list(link_map_VtoS.keys())
            if len(path_uv) == 0 and x.count((v, u)) == 0:
                curr_state_sg = temp_curr_state_sg
                energy_consumed_per_request = 0
                logging.info(f"Unable to embed all Links for VNRequest_ {vne_id + 1} VNRequest Discarded")
                # ---------------------------------Need to be printed (Start)--------------------------
                # print("Unable to embed all Links for VNRequest_", vne_id + 1, " VNRequest Discarded")
                # ---------------------------------Need to be printed (End)--------------------------
                VNE_parameters[vne_id - 1] = [0, 0, 0]
                flag = True
                break
            else:
                x = list(link_map_VtoS.keys())
                if x.count((v, u)) == 1:
                    link_map_VtoS[(u, v)] = link_map_VtoS[(v, u)]
                    continue
                else:
                    link_map_VtoS[(u, v)] = path_uv
                # ---------------------------------Need to be printed (Start)--------------------------
                # print(link_map_VtoS[(u, v)])
                # ---------------------------------Need to be printed (End)--------------------------

                for ix in range(len(path_uv) - 1):
                    # ux = int(all_path_uv[0][ix])
                    # vx = int(all_path_uv[0][ix + 1])
                    ux = path_uv[ix]
                    vx = path_uv[ix + 1]

                    # calc_BW+=(demand_uv/curr_state_sg.edge_weights[(ux, vx)])
                    # count+=1

                    set_BW.add((ux, vx))
                    set_BW.add((vx, ux))
                    curr_state_sg.edge_weights[(ux, vx)] = curr_state_sg.edge_weights[(ux, vx)] - demand_uv
                    curr_state_sg.edge_weights[(vx, ux)] = curr_state_sg.edge_weights[(vx, ux)] - demand_uv
                    sn_cost_edge += demand_uv
                # print(len(set_BW))
        if flag:
            energy_consumed_per_request=0
            continue
        if len(link_map_VtoS) == len(vne.edges):
            temp_curr_state_sg = curr_state_sg
            total_energy_consumed+=energy_consumed_per_request
            logging.info(f"Link Mapping for VNRequest_ {vne_id + 1} is completed")

            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Link Mapping for VNRequest_", vne_id + 1, " is completed")
            # ---------------------------------Need to be printed (End)--------------------------

            VNEmbed_nodes[vne_id] = mappingVtoS
            VNEmbed_edges[vne_id] = link_map_VtoS
            sn_cost = sn_cost_node + sn_cost_edge
            logging.info(f"Consumed node cost: {sn_cost_node}, Consumed edge cost: {sn_cost_edge}")
            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Consumed node cost: ", sn_cost_node, "Consumed edge cost: ", sn_cost_edge)
            # ---------------------------------Need to be printed (End)--------------------------
            VNE_parameters[vne_id - 1] = [revenue_vne, sn_cost, (revenue_vne / sn_cost)]
            accepted_req += 1
            #need changes

            for key,path in link_map_VtoS.items(): #link_map_VtoS is [(u,v):{1,3,4,6,7}]
                all_link_path_len_cur_vne.append(len(path)-1)

            #no of physical link consumed/no of total link in vne
            VNE_avgPath_len[vne_id - 1] = sum(all_link_path_len_cur_vne) / len(vne.edges)

            nodeSum_temp = nodes_sum(curr_state_sg)
            edgeSum_temp = edges_sum(curr_state_sg)
            substrate_details[vne_id] = (nodeSum_temp, edgeSum_temp)
            logging.info(f"Current state of physical graph After mapping \n  Node sum: {str(nodeSum_temp).rjust(10)} "
                         f"Edge sum: {str(edgeSum_temp).rjust(10)}\n")
            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Current state of physical graph After mapping\n" + " Node sum: " + str(nodeSum_temp).rjust(10)
                  # + " Edge sum: " + str(edgeSum_temp).rjust(10))
            # ---------------------------------Need to be printed (End)--------------------------
            # print(link_map_VtoS)
        else:
            curr_state_sg = temp_curr_state_sg
            logging.info(f"Unable to embed all links for VNRequest_ {vne_id+1}, VNRequest Discarded\n")
            # ---------------------------------Need to be printed (Start)--------------------------
            # print("Unable to embed all links for VNRequest_", vne_id + 1, " VNRequest Discarded")
            # ---------------------------------Need to be printed (End)--------------------------
        # print(vne_id)
        # ---------------------------------Need to be printed (Start)--------------------------
        # print("---------------------------------------------------------------------\n")
        # ---------------------------------Need to be printed (End)--------------------------

    end_time = datetime.now().time()
    print(f"\t\t{datetime.now().time()}\t PUVNP completed\n")
    logging.info(f" PUVNP end time : {datetime.now().time()}")
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)

    vne_total = len(vne_list)
    set_details = [vne_total, accepted_req, round(accepted_req / vne_total, 3)]
    # Link Mapping Completed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    # ---------------------------------Need to be printed (Start)--------------------------

    # **Print All Mapping from VNR to Substrate Graph**
    # for i in range(len(VNEmbed_nodes)):
    #     node_map = VNEmbed_nodes[i]
    #     edge_map = VNEmbed_edges[i]
    #
    #     print("VNReques_", i + 1)
    #     print(node_map)
    #     print(edge_map)
    #     print("----------------------------------------------\n")
    # VNE_avgPath_len
    # print("Average path length for each VNR:\n")
    # for ix in range(len(VNE_avgPath_len)):
    #     print("VN id_", str(ix + 1).rjust(2), " Avg path length: ", str(VNE_avgPath_len[ix]).rjust(5))
    # for ix in range(len(VNE_parameters)):
    #     print("VN id_ ", str(ix + 1).rjust(2), ": Revenue: ", str(VNE_parameters[ix][0]).rjust(5),
    #           " Cost: ", str(VNE_parameters[ix][1]).rjust(5), " revenue/cost ratio: ",
    #           str(VNE_parameters[ix][2]).rjust(5))
    # print()
    logging.info(f"Used links are : ")
    for t in set_BW:
        logging.info(f"{t}")
    logging.info(f"Used nodes are : ")
    for t in set_CRB:
        logging.info(f"{t}")
    logging.info(f"Set Details : ")
    logging.info(f"Total VN Request: {set_details[0]}, Number of VN Successfully Embedded: {set_details[1]}, Acceptance Ratio: {set_details[2]}\n")
    # print("Set details: ")
    # print("Total VN request: ", set_details[0], " Number of VN successfully embedded: ", set_details[1],
    #       " acceptance ratio: ", set_details[2])

    # ---------------------------------Need to be printed (End)--------------------------





    # print(len(substrate.edge_weights)//2)
    # print(len(substrate.node_weights))

    # Difference betwenn current state and orignal graph

    # print("Inital state of physical Network")
    # print("Nodes: ", substrate.nodes)
    # print("Nodes & their Weights: ", substrate.node_weights)
    # print("Edges: ", len(substrate.edges))
    # print("Edge & their Weights: ", substrate.edge_weights)
    # print("Adj List: ", substrate.neighbours)
    #
    # print("After mapping current state of physical Network")
    # print("Nodes: ", temp_curr_state_sg.nodes)
    # print("Nodes & their Weights: ", temp_curr_state_sg.node_weights)
    # print("Edges: ", len(temp_curr_state_sg.edges))
    # print("Edge & their Weights: ", temp_curr_state_sg.edge_weights)
    # print("Adj List: ", temp_curr_state_sg.neighbours)




    # Parameters Calculations
    total_revenue = 0
    total_cost = 0
    tota_cr = 0
    for abc in  VNE_parameters:
        total_revenue += abc[0]
        total_cost += abc[1]

    if total_cost != 0:
        tota_cr = (total_revenue/total_cost)

    postResource = nodes_sum(curr_state_sg) + edges_sum(curr_state_sg)
    # postResource = 0
    # xflag = True
    # for rs in substrate_details:
    #     if xflag:
    #         xflag = False
    #         continue
    #     if rs != (-1, -1):
    #         postResource = (rs[0] + rs[1])

    t_node = 0
    for vne in vne_list:
        t_node += vne.nodes

    t_link = 0
    for vne in vne_list:
        t_link += len(vne.edges)

    t_bw = 0
    t_crb = 0
    for id, val in HRR.items():
        t_crb += val[1] / vne_list[id].nodes
        t_bw += 2*val[2] / len(vne_list[id].edges)



    avg_bw = 0
    # if (len(set_BW) != 0):
    #     # avg_bw = (calc_BW / (len(set_BW)// 2)) * 100
    #     avg_bw = (calc_BW / (len(set_BW) // 2)) * 100

    avg_crb = 0
    # if (len(set_CRB) != 0):
    #     avg_crb = (calc_CRB / len(set_CRB)) * 100

    # print(calc_BW)
    # print(len(set_BW) // 2)
    # print(calc_CRB)
    # print(len(set_CRB))

    calc_BW=0
    calc_CRB=0

    linkUtilized=0
    for edge in (substrate.edges):
        if curr_state_sg.edge_weights[edge]!=substrate.edge_weights[edge]:
            linkUtilized+=1
            calc_BW += ((int(substrate.edge_weights[edge])-int(curr_state_sg.edge_weights[edge]))/int(substrate.edge_weights[edge]))
            # print(calc_BW)
    # print(calc_BW)
    # print(linkUtilized)
    if linkUtilized!=0:
        avg_bw= (calc_BW/2)/(linkUtilized/2)

    nodeUtilized = 0
    for node in range(substrate.nodes):
        if int(curr_state_sg.node_weights[node]) != int(substrate.node_weights[node]):
            # print(curr_state_sg.node_weights[node])
            # print(substrate.node_weights[node])

            nodeUtilized += 1
            calc_CRB += ((int(substrate.node_weights[node]) - int(curr_state_sg.node_weights[node])) / int(substrate.node_weights[node]))
            # print(nodeUtilized)
            # print(t)
            # print(calc_CRB)
            # print()
    # print(calc_CRB)
    if nodeUtilized != 0:
        avg_crb = (calc_CRB) / (nodeUtilized)
    # print(nodeUtilized)
    # print(avg_crb)

    output_dict = {
        "algorithm": "DAA",
        "revenue": total_revenue,
        "total_cost": total_cost,
        "revenuetocostratio": tota_cr,
        "accepted": set_details[1],
        "total_request": set_details[0],
        "embeddingratio": set_details[2],
        "pre_resource": preResource,
        "post_resource": postResource,
        "consumed": (preResource - postResource),
        "avg_bw": avg_bw*100,
        "avg_crb": avg_crb*100,
        "avg_link": ((len(set_BW)//2)/(len(substrate.edge_weights)//2))*100,
        "avg_node": (len(set_CRB)/len(substrate.node_weights))*100,
        "avg_path": sum(VNE_avgPath_len)/accepted_req,
        "avg_exec": (duration),
        "No_of_Links_used": len(set_BW) // 2,  # (utilized_links // 2),
        "No_of_Nodes_used": len(set_CRB),  # (utilized_nodes),
        "total_nodes": t_node,
        "total_links": t_link//2,
        "Energy_Consumed": total_energy_consumed
    }

    return output_dict

if __name__ == '__main__':
    main()









