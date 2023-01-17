import helper
import copy
from datetime import datetime, date
import logging
import random
from rethinking_helper import *
import config

def main():
    print(f"\t\t{datetime.now().time()}\tRethinking started")
    # substrate, vne_list = helper.read_pickle()
    substrate, vne_list = copy.deepcopy(config.substrate), copy.deepcopy(config.vne_list)
    copy_sub = copy.deepcopy(substrate)
    logging.basicConfig(filename="rethinking.log", filemode="w", level=logging.INFO)
    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK (BEFORE MAPPING VNRs)")
    logging.info(
        f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} "
    )
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge, substrate.edge_weights[edge]))
    logging.info(
        f"\t\tEdges of the substrate network with weight are : {temp}\n\n\t\t\t\t\t\tVIRTUAL NETWORK"
    )

    total_vnr_nodes = 0
    total_vnr_links = 0
    logging.info(f"\t\tTotal number of Virtual Network Request is : {len(vne_list)}\n")
    for vnr in range(len(vne_list)):
        logging.info(
            f"\t\tTotal number of nodes and edges in VNR-{vnr} is : {vne_list[vnr].nodes} and {len(vne_list[vnr].edges)}"
        )
        temp = []
        total_vnr_nodes += vne_list[vnr].nodes
        for node in range(vne_list[vnr].nodes):
            temp.append((node, vne_list[vnr].node_weights[node]))
        logging.info(f"\t\tNodes of the VNR-{vnr} with weight are : {temp}")
        temp = []
        total_vnr_links += len(vne_list[vnr].edges)
        for edge in vne_list[vnr].edges:
            temp.append((edge, vne_list[vnr].edge_weights[edge]))
        if vnr == len(vne_list) - 1:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}\n\n")
        else:
            logging.info(f"\t\tEdges of the VNR-{vnr} with weight are : {temp}")

    start_time = datetime.now().time()
    accepted = 0
    revenue = 0
    path_cnt =0 
    avg_path_length = 0
    avg_path_length_modified = 0
    curr_map = dict()  # only contains the requests which are successfully mapped
    pre_resource_edgecost = (
        sum(substrate.edge_weights.values()) // 2
    )  # total available bandwidth of the physical network
    pre_resource_nodecost = sum(
        substrate.node_weights.values()
    )  # total crb bandwidth of the physical network
    pre_resource = pre_resource_edgecost + pre_resource_nodecost

    req_order = list(range(len(vne_list)))
    random.shuffle(req_order)
    cnt = 0
    for req_no in req_order:
        cnt += 1
        # if cnt%5==0:
        #     print(f"\t\t\t{cnt}")
        req_map = node_map(copy.deepcopy(substrate), vne_list[req_no], req_no)
        if req_map is None:
            logging.warning(f"\t\tNode mapping not possible for req no {req_no}\n\n\n")
            continue
        else:
            logging.info(f"\tNode embedding is done for {req_no}:::{req_map}")
        req_map = temp_map(vne_list, req_no, req_map)
        # [[PATH for edge 1], [PATH for edge 2]]
        population = edge_map(substrate, vne_list[req_no], req_no, req_map, vne_list)
        initial_population = []
        if population is None or len(population) == 0:
            logging.warning(f"\t\tinitial population can't be generated for request no : {req_no}\n\n\n")
            continue
        population_set = set()
        for i in population:
            abhi_map = i
            abhi_map.edge_map = i.edge_map
            j = 0
            for edge in vne_list[req_no].edges:
                if int(edge[0]) > int(edge[1]):
                    abhi_map.edges.append(edge)
                    abhi_map.edge_weight.append(vne_list[req_no].edge_weights[edge])
                    abhi_map.path_cost.append(
                        vne_list[req_no].edge_weights[edge] * (len(abhi_map.edge_map[j])-1)
                    )
                    abhi_map.edge_cost += abhi_map.edge_weight[j] * (len(
                        abhi_map.edge_map[j]
                    ) - 1)
                    j += 1
            abhi_map.total_cost = abhi_map.node_cost + abhi_map.edge_cost
            abhi_map.fitness = get_fitness(abhi_map, vne_list[req_no])
            initial_population.append(abhi_map)
            population_set.add(get_hashable_map(abhi_map))
        logging.info(f"\t\tInitial_population for req no: {req_no}::::")
        for i in initial_population:
            logging.info(f"\t\t\t{i.edge_map}\tfitness: {i.fitness:.4f}\t tot_cost: {i.total_cost}")
        logging.info(f"\n\n")
        elite_population = copy.deepcopy(initial_population)
        if len(elite_population) > 1:
            for _ in range(8):
                logging.info(f"\t\t\t\t ITERATION {_}")
                i = 0
                while i < 8:
                    i += 1
                    parent1, parent2 = tournament_selection( # check it for random selection
                        elite_population, vne_list, req_no
                    )
                    child1, child2 = elastic_crossover(
                        copy.deepcopy(parent1), copy.deepcopy(parent2), population_set, substrate, vne_list[req_no], i, elite_population
                    )   # last argument i is for identify which inside loop
                    if child1 is not None: 
                        mutate(
                            copy.deepcopy(child1), substrate, population_set, vne_list[req_no], i, elite_population
                        ) # last argument i is for identify which inside loop
                    if child2 is not None:
                        mutate(
                            copy.deepcopy(child2), substrate, population_set, vne_list[req_no], i, elite_population
                        )
                elite_population, population_set = import_elite(elite_population)
                logging.info(f"")
                logging.info(f"\t\t\telite population after iteration {_}")
                for i in elite_population:
                    logging.info(f"\t\t\t{i.edge_map}\tfitness: {i.fitness:.4f}\ttot_cost: {i.total_cost}")
                logging.info(f"")
        selected_map = get_best_map(elite_population)
        
        logging.info(f"\n")
        ls = dict()
        c =0
        path_count_modified = 0
        for ed in selected_map.edges:
            ls[ed] = selected_map.edge_map[c]
            path_count_modified += (len(selected_map.edge_map[c]) - 1)
            c += 1
        avg_path_length_modified += path_count_modified / (len(vne_list[req_no].edges)//2)
        logging.info(f"\t\tThe selected chromosome for VNR {req_no} is {selected_map.edge_map}\tfitness: {selected_map.fitness:.4f}\ttot_cost: {selected_map.total_cost}")
        logging.info(f"\t\tThe node map of VNR {req_no} is {selected_map.node_map}")
        logging.info(f"\t\tThe edge map of VNR {req_no} is {ls}")
        
        sub_wt = []
        sorder = sorted(
            [a for a in range(substrate.nodes)],
            key=lambda x: substrate.node_weights[x]
        )
        for node in sorder:
            sub_wt.append((node, substrate.node_weights[node]))
        logging.info(f"\t\tSubstrate node before mapping VNR-{req_no} is {sub_wt}")
        sub_wt = []
        sorder = sorted(
            [a for a in substrate.edges],
            key=lambda x: substrate.edge_weights[x],
        )
        for edge in sorder:
            sub_wt.append((edge, substrate.edge_weights[edge]))
        logging.info(f"\t\tSubstrate edge before mapping VNR-{req_no} is {sub_wt}")

        substract_from_substrate(substrate, vne_list[req_no], selected_map)
        
        sub_wt = []
        sorder = sorted(
            [a for a in range(substrate.nodes)],
            key=lambda x: substrate.node_weights[x]
        )
        for node in sorder:
            sub_wt.append((node, substrate.node_weights[node]))
        logging.info(f"\t\tSubstrate after mapping VNR-{req_no} is {sub_wt}")
        sub_wt = []
        sorder = sorted(
            [a for a in substrate.edges],
            key=lambda x: substrate.edge_weights[x],
        )
        for edge in sorder:
            sub_wt.append((edge, substrate.edge_weights[edge]))
        logging.info(f"\t\tSubstrate edge after mapping VNR-{req_no} is {sub_wt}")

        accepted += 1
        avg_path_length += findAvgPathLength(vne_list[req_no])
        curr_map[req_no] = selected_map
        for ed in req_map.edge_map:
            path_cnt += len(req_map.edge_map[ed])
        
        revenue += sum(vne_list[req_no].node_weights.values()) + sum(vne_list[req_no].edge_weights.values())//2

        logging.info(f"\n\n")

    ed_cost = 0
    no_cost = 0
    for request in curr_map.values():
        ed_cost += request.edge_cost  # total bandwidth for all the mapped requests
        no_cost += request.node_cost  # total crb for all the mapped requests


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

    if (accepted != 0):
        avg_path_length /= accepted
        avg_path_length_modified /= accepted
    post_resource = post_resource_edgecost + post_resource_nodecost
    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(
        date.min, start_time
    )

    #print(f"\n\nThe revenue is {revenue} and total cost is {tot_cost}")
    #print(f"Total number of requests embedded is {accepted}")
    #print(f"Embedding ratio is {accepted/len(vne_list)}")
    #print(f"Availabe substrate resources before mapping is {pre_resource}")
    #print(f"Consumed substrate resources after mapping is {pre_resource - post_resource}")
    #print(f"Average link utilization {ed_cost/pre_resource_edgecost}")
    #print(f"Average node utilization {no_cost/pre_resource_nodecost}")
    #print(f"Average execution time {duration/len(vne_list)}")

    logging.info(f"\n\n\t\t\t\t\t\tSUBSTRATE NETWORK AFTER MAPPING VNRs")
    logging.info(
        f"\t\tTotal number of nodes and edges in substrate network is : {substrate.nodes} and {len(substrate.edges)} "
    )
    temp = []
    for node in range(substrate.nodes):
        temp.append((node, substrate.node_weights[node]))
    logging.info(f"\t\tNodes of the substrate network with weight are : {temp}")
    temp = []
    for edge in substrate.edges:
        temp.append((edge, substrate.edge_weights[edge]))
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
            "No_of_Links_used": -1,
            "avg_node": -1,
            "No_of_Nodes_used": -1,
            "avg_path": -1,
            "avg_exec": (duration),
            "total_nodes": total_vnr_nodes,
            "total_links": total_vnr_links//2,
        }
        print(f"\t\t{datetime.now().time()}\trethinking completed\n")
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
    logging.info(f"\t\tAverage Path length is {avg_path_length_modified:.4f}")
    # logging.info(f"\t\tAverage BW utilization {(ed_cost/pre_resource_edgecost)*100:.4f}%")
    # logging.info(f"\t\tAverage CRB utilization {(no_cost/pre_resource_nodecost)*100:.4f}%")
    logging.info(f"\t\tAverage execution time {duration/len(vne_list)} (HH:MM:SS)\n\n\n")
    # logging.shutdown()
    output_dict = {
        "revenue": revenue,
        "total_cost": tot_cost,
        "accepted": accepted,
        "total_request": len(vne_list),
        "pre_resource": pre_resource,
        "post_resource": post_resource,
        "avg_bw": (average_edge_utilization)*100,
        "avg_crb": (average_node_utilization)*100,
        "avg_link": ((utilized_links/len(substrate.edge_weights))/2)*100,
        "No_of_Links_used": (utilized_links//2),
        "avg_node": (utilized_nodes/len(substrate.node_weights))*100,
        "No_of_Nodes_used": (utilized_nodes),
        "avg_path": avg_path_length_modified,
        "avg_exec": (duration),
        "total_nodes": total_vnr_nodes,
        "total_links": total_vnr_links//2,
    }
    print(f"\t\t{datetime.now().time()}\tRethinking completed\n")
    return output_dict


if __name__ == "__main__":
    main()
