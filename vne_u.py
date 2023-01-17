import networkx as nx
import random
import graph_u
from graph_u import Parameters
import numpy as np

def create_vne(min_nodes=2, max_nodes=10, no_requests=1000, probability=0.4):
    random_node_list = [
        random.randint(min_nodes, max_nodes) for i in range(no_requests)
    ]
    new_vne_req = []
# def create_vne(min_nodes=2, max_nodes=3, no_requests=1000, probability=0.4):
#     random_node_list_arr = np.random.uniform(min_nodes, max_nodes, no_requests)
#     random_node_list = [round(i) for i in random_node_list_arr]
#     new_vne_req = []
    for req in random_node_list:
        G = nx.erdos_renyi_graph(req, probability, directed=False)
        ng = nx.to_dict_of_lists(G)
        g = {}
        for i in ng:
            g[i + 1] = []
            for j in ng[i]:
                g[i + 1].append(j + 1)

        if not nx.is_connected(G):
            null_node_list = [key for key, val in g.items() if not val]
            graph_node_count = {_key: len(_val) for _key, _val in g.items()}
            sorted_dict_list = sorted(
                graph_node_count.items(), key=lambda x: x[1], reverse=True
            )
            if len(null_node_list) != len(g):
                for index, empty_node in enumerate(null_node_list):
                    g[sorted_dict_list[index][0]].append(empty_node)
                    g[empty_node].append(sorted_dict_list[index][0])
            else:
                for i in range(len(g)):
                    for j in range(len(g) - i - 1):
                        if null_node_list[j + 1] not in g[null_node_list[j]]:
                            g[null_node_list[j]].append(null_node_list[j + 1])
                        if null_node_list[j] not in g[null_node_list[j + 1]]:
                            g[null_node_list[j + 1]].append(null_node_list[j])
        new_vne_req.append(g)

    # print("new VNE REQ is",new_vne_req)
    vne = []
    for i in range(len(new_vne_req)):
        edges = set()
        nodes = len(new_vne_req[i])
        for j in range(nodes):
            for k in new_vne_req[i][j + 1]:
                edges.add((str(j), str(k - 1)))
        vne.append(graph_u.Graph(nodes, edges, Parameters(1, 5, 1, 10, 0, 100, 0, 100, 1, 4, 1, 10, 5, 50)))
        #vne.append(graph_u.Graph(nodes, edges, Parameters(1,5,1,10,0,100,0,100,1,4,1,10,5,50)) )  # 0,100, 0,100, 1,4for vne request BW ,CRB, Location,Delay
    #print (vne)# xy 50-100 D 2-2
    return vne


if __name__ == "__main__":
    create_vne()
