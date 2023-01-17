# this module will parse the pickle file
import logging
import pickle, copy
from statistics import mode

from numpy import outer
#import embedder
import embedderDirect
import networkx as nx
import random
import os, sys
import helper
from datetime import datetime, date
import config
def main():
    logging.info(f"\n\n\t\t\t\t\t\tVNE-Stable and Direct approach Started")
    print(f"\t\t{datetime.now().time()}\tParser Started")
    # #print the out put in log file#print
    # FORMAT = '%(asctime)s - %(levelname)s: %(message)s'
    FORMAT = '%(levelname)s: %(message)s'
    logging.basicConfig(filename=r'parser.log',
                        filemode="w",
                        format=FORMAT,
                        level=logging.DEBUG,
                        datefmt = '%Y-%m-%d %H:%M:%S %p')

    # substrate, vne_list = helper.read_pickle()
    substrate, vne_list = copy.deepcopy(config.substrate), copy.deepcopy(config.vne_list)
    sn = dict()
    vneRequests = list()

    # this part will parse the substrate network
    nodes = list(range(substrate.nodes))
    edges = list(substrate.edges)
    #print("#printing nodes/edges")
    #print(nodes)
    #print(edges)
    for i in nodes:
        sn[int(i)+1] = list()

    for i in edges:
        sn[int(i[0])+1].append(int(i[1])+1)
        
    # this part will parse the vne requests
    #print("contents of list(i.nodes) amd list (i.edges)")
    for i in vne_list:
        vne = dict()
        node = list(range(i.nodes))
        #print("contents of list(i.nodes) in side for loop")
        #print()
        #print(i.nodes)
        edge = list(i.edges)
        #print("contents of list (i.edges) in side for loop")
        #print(i.edges)
        for j in node:
            vne[int(j)+1] = set()
        for j in edge:
            vne[int(j[0])+1].add(int(j[1])+1)
            vne[int(j[1])+1].add(int(j[0])+1)
        for j in vne:
            vne[j] = list(vne[j])
        vneRequests.append(vne)

    logging.info("Printing SN") #KK
    logging.info(sn)
    logging.info("Printing vneRequests")
    # logging.info(new_vne_req)
    logging.info(vneRequests)
    # calling form embedderdirect will cal  page rank(Stable method) and them noderank(Directmethod)
    start_time = datetime.now().time()
    output = embedderDirect.calling(start_time, sn,vneRequests, substrate, vne_list)


    #print("***************************************************************************************************")
    #print(output[0]["total_cost"])
    #print(output[1]["total_cost"])
    logging.info(f"\n\n\t\t\t\t\t\tVNE-Stable and Direct approach Completed")
    print(f"\t\t{datetime.now().time()}\tParser completed\n")
    return output
if __name__ == "__main__":
    main()