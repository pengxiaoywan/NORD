import pickle
with open('input.pickle', 'rb') as handle:
    b = pickle.load(handle)

sn_graph=b.et("substrate")
nodes_sn_graph=sn_graph.nodes
print(nodes_sn_graph)

SN_node_CRB=sn_graph.node_weights
SN_edge_BW=sn_graph.edge_weights
print(SN_node_CRB)
print(SN_edge_BW)