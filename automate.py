import copy
import os
from time import sleep
import pandas as pd
from greedy import main as greedy
from parserr import main as parserr
from rethinking import main as rethinking
import time
from topsis_updated import main as topsis
from nrm import main as NRM
from Rematch_AHP import main as Rematch_AHP
from Puvnp import main as Puvnp
from vne_u import create_vne as vne_u
import graph_extraction_uniform
import logging
import config
import pickle

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    # formatter = logging.Formatter('%(asctime)s %(levelname)s  : %(message)s')
    formatter = logging.Formatter('[%(levelname)s] : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler) 

output_dict = {
        "algorithm": [],
        "revenue": [],
        "total_cost" : [],
        "revenuetocostratio":[],
        "accepted" : [],
        "total_request": [],
        "embeddingratio":[],
        "pre_resource": [],
        "post_resource": [],
        "consumed":[],
        "avg_bw": [],
        "avg_crb": [],
        "avg_link": [],
        "No_of_Links_used": [],
        "avg_node": [],
        "No_of_Nodes_used": [],
        "avg_path": [],
        "avg_exec": [],
        "total_nodes": [],
        "total_links": [],
    }

def exec_greedy(tot=1):
    gred_out = greedy()
    sleep(tot*1)
    
    printToExcel(
        algorithm='GREEDY',
        revenue=gred_out['revenue'],
        total_cost=gred_out['total_cost'],
        revenuetocostratio=(gred_out['revenue']/gred_out['total_cost'])*100,
        accepted=gred_out['accepted'],
        total_request=gred_out['total_request'],
        embeddingratio=(gred_out['accepted']/gred_out['total_request'])*100,
        pre_resource=gred_out['pre_resource'],
        post_resource=gred_out['post_resource'],
        consumed=gred_out['pre_resource']-gred_out['post_resource'],
        avg_bw=gred_out['avg_bw'],
        avg_crb=gred_out['avg_crb'],
        avg_link=gred_out['avg_link'],
        No_of_Links_used=gred_out['No_of_Links_used'],
        avg_node=gred_out['avg_node'],
        No_of_Nodes_used=gred_out['No_of_Nodes_used'],
        avg_path=gred_out['avg_path'],
        avg_exec=gred_out['avg_exec'].total_seconds()*1000/gred_out['total_request'],
        total_nodes=gred_out['total_nodes'],
        total_links=gred_out['total_links']
    )




def exec_topsis(tot=1):
    topsis_out = topsis()
    sleep(tot*1)
    
    printToExcel(
        algorithm='TOPSIS',
        revenue=topsis_out['revenue'],
        total_cost=topsis_out['total_cost'],
        revenuetocostratio=(topsis_out['revenue']/topsis_out['total_cost'])*100,
        accepted=topsis_out['accepted'],
        total_request=topsis_out['total_request'],
        embeddingratio=(topsis_out['accepted']/topsis_out['total_request'])*100,
        pre_resource=topsis_out['pre_resource'],
        post_resource=topsis_out['post_resource'],
        consumed=topsis_out['pre_resource']-topsis_out['post_resource'],
        avg_bw=topsis_out['avg_bw'],
        avg_crb=topsis_out['avg_crb'],
        avg_link=topsis_out['avg_link'],
        No_of_Links_used=topsis_out['No_of_Links_used'],
        avg_node=topsis_out['avg_node'],
        No_of_Nodes_used=topsis_out['No_of_Nodes_used'],
        avg_path=topsis_out['avg_path'],
        avg_exec=topsis_out['avg_exec'].total_seconds()*1000/topsis_out['total_request'],
        total_nodes=topsis_out['total_nodes'],
        total_links=topsis_out['total_links']
    )

def exec_parserr(tot=2):
    parser_out = parserr()
    sleep(tot*2)
    
    printToExcel(
        algorithm='PAGERANK-STABLE',
        revenue=parser_out[0]['revenue'],
        total_cost=parser_out[0]['total_cost'],
        revenuetocostratio=(parser_out[0]['revenue']/parser_out[0]['total_cost'])*100,
        accepted=parser_out[0]['accepted'],
        total_request=parser_out[0]['total_request'],
        embeddingratio=(parser_out[0]['accepted']/parser_out[0]['total_request'])*100,
        pre_resource=parser_out[0]['pre_resource'],
        post_resource=parser_out[0]['post_resource'],
        consumed=parser_out[0]['pre_resource']-parser_out[0]['post_resource'],
        avg_bw=parser_out[0]['avg_bw'],
        avg_crb=parser_out[0]['avg_crb'],
        avg_link=parser_out[0]['avg_link'],
        No_of_Links_used=parser_out[0]['No_of_Links_used'],
        avg_node=parser_out[0]['avg_node'],
        No_of_Nodes_used=parser_out[0]['No_of_Nodes_used'],
        avg_path=parser_out[0]['avg_path'],
        avg_exec=parser_out[0]['avg_exec'].total_seconds()*1000/parser_out[0]['total_request'],
        total_nodes=parser_out[0]['total_nodes'],
        total_links=parser_out[0]['total_links']
    )
    
    printToExcel(
        algorithm='PAGERANK-DIRECT',
        revenue=parser_out[1]['revenue'],
        total_cost=parser_out[1]['total_cost'],
        revenuetocostratio=(parser_out[1]['revenue']/parser_out[1]['total_cost'])*100,
        accepted=parser_out[1]['accepted'],
        total_request=parser_out[1]['total_request'],
        embeddingratio=(parser_out[1]['accepted']/parser_out[1]['total_request'])*100,
        pre_resource=parser_out[1]['pre_resource'],
        post_resource=parser_out[1]['post_resource'],
        consumed=parser_out[1]['pre_resource']-parser_out[1]['post_resource'],
        avg_bw=parser_out[1]['avg_bw'],
        avg_crb=parser_out[1]['avg_crb'],
        avg_link=parser_out[1]['avg_link'],
        No_of_Links_used=parser_out[1]['No_of_Links_used'],
        avg_node=parser_out[1]['avg_node'],
        No_of_Nodes_used=parser_out[1]['No_of_Nodes_used'],
        avg_path=parser_out[1]['avg_path'],
        avg_exec=parser_out[1]['avg_exec'].total_seconds()*1000/parser_out[1]['total_request'],
        total_nodes=parser_out[1]['total_nodes'],
        total_links=parser_out[1]['total_links']
    )



def exec_rethinking(tot=15):
    rethinking_out = rethinking()
    sleep(tot*4)

    printToExcel(
        algorithm='RETHINKING',
        revenue=rethinking_out['revenue'],
        total_cost=rethinking_out['total_cost'],
        revenuetocostratio=(rethinking_out['revenue']/rethinking_out['total_cost'])*100,
        accepted=rethinking_out['accepted'],
        total_request=rethinking_out['total_request'],
        embeddingratio=(rethinking_out['accepted']/rethinking_out['total_request'])*100,
        pre_resource=rethinking_out['pre_resource'],
        post_resource=rethinking_out['post_resource'],
        consumed=rethinking_out['pre_resource']-rethinking_out['post_resource'],
        avg_bw=rethinking_out['avg_bw'],
        avg_crb=rethinking_out['avg_crb'],
        avg_link=rethinking_out['avg_link'],
        No_of_Links_used=rethinking_out['No_of_Links_used'],
        avg_node=rethinking_out['avg_node'],
        No_of_Nodes_used=rethinking_out['No_of_Nodes_used'],
        avg_path=rethinking_out['avg_path'],
        avg_exec=rethinking_out['avg_exec'].total_seconds()*1000/rethinking_out['total_request'],
        total_nodes=rethinking_out['total_nodes'],
        total_links=rethinking_out['total_links']
    )

def exec_NRM(tot=15):
    NRM_out = NRM()
    sleep(tot*4)

    printToExcel(
        algorithm='NRM',
        revenue=NRM_out['revenue'],
        total_cost=NRM_out['total_cost'],
        revenuetocostratio=(NRM_out['revenue']/NRM_out['total_cost'])*100,
        accepted=NRM_out['accepted'],
        total_request=NRM_out['total_request'],
        embeddingratio=(NRM_out['accepted']/NRM_out['total_request'])*100,
        pre_resource=NRM_out['pre_resource'],
        post_resource=NRM_out['post_resource'],
        consumed=NRM_out['pre_resource']-NRM_out['post_resource'],
        avg_bw=NRM_out['avg_bw'],
        avg_crb=NRM_out['avg_crb'],
        avg_link=NRM_out['avg_link'],
        No_of_Links_used=NRM_out['No_of_Links_used'],
        avg_node=NRM_out['avg_node'],
        No_of_Nodes_used=NRM_out['No_of_Nodes_used'],
        avg_path=NRM_out['avg_path'],
        avg_exec=NRM_out['avg_exec'].total_seconds()*1000/NRM_out['total_request'],
        total_nodes=NRM_out['total_nodes'],
        total_links=NRM_out['total_links']
    )
def exec_Rematch(tot=15):
    AHP_out = Rematch_AHP()
    sleep(tot*4)

    printToExcel(
        algorithm='Rematch',
        revenue=AHP_out['revenue'],
        total_cost=AHP_out['total_cost'],
        revenuetocostratio=(AHP_out['revenue']/AHP_out['total_cost'])*100,
        accepted=AHP_out['accepted'],
        total_request=AHP_out['total_request'],
        embeddingratio=(AHP_out['accepted']/AHP_out['total_request'])*100,
        pre_resource=AHP_out['pre_resource'],
        post_resource=AHP_out['post_resource'],
        consumed=AHP_out['pre_resource']-AHP_out['post_resource'],
        avg_bw=AHP_out['avg_bw'],
        avg_crb=AHP_out['avg_crb'],
        avg_link=AHP_out['avg_link'],
        No_of_Links_used=AHP_out['No_of_Links_used'],
        avg_node=AHP_out['avg_node'],
        No_of_Nodes_used=AHP_out['No_of_Nodes_used'],
        avg_path=AHP_out['avg_path'],
        avg_exec=AHP_out['avg_exec'].total_seconds()*1000/AHP_out['total_request'],
        total_nodes=AHP_out['total_nodes'],
        total_links=AHP_out['total_links']
    )

def exec_puvnp(tot=15):

    puvnp_out = Puvnp()
    sleep(tot*4)

    printToExcel(
        algorithm='PUVNP',
        revenue=puvnp_out  ['revenue'],
        total_cost=puvnp_out ['total_cost'],
        revenuetocostratio=(puvnp_out ['revenue']/puvnp_out ['total_cost'])*100,
        accepted=puvnp_out ['accepted'],
        total_request=puvnp_out ['total_request'],
        embeddingratio=(puvnp_out ['accepted']/puvnp_out ['total_request'])*100,
        pre_resource=puvnp_out ['pre_resource'],
        post_resource=puvnp_out ['post_resource'],
        consumed=puvnp_out ['pre_resource']-puvnp_out ['post_resource'],
        avg_bw=puvnp_out ['avg_bw'],
        avg_crb=puvnp_out ['avg_crb'],
        avg_link=puvnp_out ['avg_link'],
        No_of_Links_used=puvnp_out ['No_of_Links_used'],
        avg_node=puvnp_out ['avg_node'],
        No_of_Nodes_used=puvnp_out ['No_of_Nodes_used'],
        avg_path=puvnp_out ['avg_path'],
        avg_exec=puvnp_out ['avg_exec'].total_seconds()*1000/puvnp_out ['total_request'],
        total_nodes=puvnp_out ['total_nodes'],
        total_links=puvnp_out ['total_links']
    )

def printToExcel(algorithm='', revenue='', total_cost='', revenuetocostratio='', accepted='', total_request='', 
embeddingratio='', pre_resource='', post_resource='',consumed='',avg_bw='',avg_crb='',avg_link='',No_of_Links_used='',
avg_node='',No_of_Nodes_used='',avg_path='',avg_exec='', total_nodes='', total_links=''):

    output_dict["algorithm"].append(algorithm)
    output_dict["revenue"].append(revenue)
    output_dict["total_cost"].append(total_cost)
    output_dict["revenuetocostratio"].append(revenuetocostratio)
    output_dict["accepted"].append(accepted)
    output_dict["total_request"].append(total_request)
    output_dict["embeddingratio"].append(embeddingratio)
    output_dict["pre_resource"].append(pre_resource)
    output_dict["post_resource"].append(post_resource)
    output_dict["consumed"].append(consumed)
    output_dict["avg_bw"].append(avg_bw)
    output_dict["avg_crb"].append(avg_crb)
    output_dict["avg_link"].append(avg_link)
    output_dict["No_of_Links_used"].append(No_of_Links_used)
    output_dict["avg_node"].append(avg_node)
    output_dict["No_of_Nodes_used"].append(No_of_Nodes_used)
    output_dict["avg_path"].append(avg_path)
    output_dict["avg_exec"].append(avg_exec)
    output_dict["total_nodes"].append(total_nodes)
    output_dict["total_links"].append(total_links)

    addToExcel()

def addToExcel():
    geeky_file = open('geekyfile.pickle', 'wb')
    pickle.dump(output_dict, geeky_file)
    geeky_file.close()

def main(substrate, vne):
    tot=0
    ls = [250, 500, 750, 1000]
    for req_no in ls:
        tot += 1
        print(f"\n\treq_no: {req_no}\n")
        # setup_logger('log1','vikor.log')
        # setup_logger('log2','greedy.log')
        # try:
        #     iteration = int(input("Enter how many times to repeat (int only) : "))
        # except:
        #     iteration = 1
        iteration = 10
        iteration = max(iteration, 1)
        cnt=0
        while cnt<iteration:
            vne_list = vne(no_requests=req_no)
            config.substrate = copy.deepcopy(substrate)
            config.vne_list = copy.deepcopy(vne_list)

            # Uncomment those functions which to run, comment all other. for ex if want to run greedy algorithm only leave
            # exec_greedy() uncommented and comment all other (exec_topsis(), exec_parser(),  exec_rethinking())
            
            exec_greedy(tot)        #Runs GREEDY algorithm

            exec_topsis(tot)        #Runs NORD algorithm

            exec_parserr(tot)        #Runs PARSER algorithm

            exec_rethinking(tot)    #Runs RETHINKING algorithm
            exec_NRM(tot)
            exec_Rematch(tot)
            exec_puvnp(tot)  # PUVNP
            
            if((cnt+1)%2==0):
                print(f'\n\tFor REQUEST {req_no} ITERATION {cnt+1} COMPLETED\n\n')
            printToExcel()
            cnt += 1
    

#######################################################################################
#######################################################################################
##                                                                                   ##
##    IMPORTANT - CLOSE Results.xlsx (excel file) IF OPEN BEFORE RUNNING THIS           ##
##                                                                                   ##
##    IMPORTANT - PLEASE CHOOSE THE PICKLE FILE, CRB & BW LIMITS FOR                 ##  
##                UNIFORM DISTRIBUTIONS BEFORE RUNNING THIS   ##
##                                                                                   ##
#######################################################################################
#######################################################################################
def generateSubstrate(for_automate, pickle_name):
    substrate, _ = for_automate(1)
    geeky_file = open(pickle_name, 'wb')
    pickle.dump(substrate, geeky_file)
    geeky_file.close()

def extractSubstrate(pickle_file):
    filehandler = open(pickle_file, 'rb')
    substrate = pickle.load(filehandler)
    return substrate




def runUniformExtraction(pickle_name):
    time.sleep(10)
    substrate = extractSubstrate(str(pickle_name))
    printToExcel()
    for _ in range(3):
        printToExcel(pre_resource='UNIFORM')
    printToExcel()
    print("\nUNIFORM Extraction\n")    
    main(substrate, vne_u)



if __name__ == "__main__":

    file_exists = os.path.exists('1_random.pickle') or os.path.exists('1_uniform.pickle') or os.path.exists('1_poission.pickle') or os.path.exists('1_normal.pickle')
    print(file_exists)
    # file_exists = False       #Manually set, if want to update a substrate pickle
    if(file_exists==False):

        generateSubstrate(graph_extraction_uniform.for_automate, str(1)+'_uniform.pickle')    #Uniform Distribution



    runUniformExtraction('1_uniform.pickle')

    
    excel = pd.DataFrame(output_dict)
    excel.to_excel("Results.xlsx")
