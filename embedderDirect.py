# direct method

import nodeRankCal
import euclideanDistanceCal
import random
import pageRank
import math
import copy
import logging
from datetime import datetime, date
log = logging.getLogger(__name__)

# This function will sort the node of network according to their rank
# and returns the list containing the node in ascending order
# each index of list will contain node name ( which is actually the number assigned to the node)
def nodeSort(nodeRank):
    ans = list()
    for i in nodeRank:
        ans.append(i)
    # I am using bubbleSort but will use mergeSort while Optimizing
    for i in range(len(ans)):
        for j in range(len(ans)-1):
            if(float(nodeRank[ans[j]]['rank'])>float(nodeRank[ans[j+1]]['rank'])):
                ans[j],ans[j+1]=ans[j+1],ans[j]
                # temp = ans[j]
                # ans[j] = ans[j+1]
                # ans[j+1] = temp
    return ans

def generateLR(vneRequest):
    lr = dict()
    for i in vneRequest:
        lr[i]=random.uniform(3,8) #3-8
        #lr[i] = random.randint(3,8) # initially 3,8
    return lr

def eucDis(subLoc, vneLoc):
    x1 = subLoc[0]
    x2 = vneLoc[0]
    y1 = subLoc[1]
    y2 = vneLoc[1]
    E_LOC=math.sqrt((((x1-x2)**2)+((y1-y2)**2)))
    return E_LOC


# this is a utility function to copy dictionary
# warning do not use nested dictionary in this function
def _copy(CRB):
    ans = dict()
    for i in CRB:
        ans[i] = CRB[i]
    return ans

# this is the utility function for findShortestPath
def minDistance(arr,dist):
    mn = 0
    for i in range(len(arr)):
        if(dist[arr[i]]<dist[arr[mn]]):
            mn = i
    return mn

# this is the utility function for findShortestPath
def remove(arr,temp):
    ans = list()
    for i in range(len(arr)):
        if(i == temp):
            continue
        ans.append(arr[i])
    return ans

# this function will update linkBandWidth
def updateLinkBandWidth(linkBandWidth, parent, reqLinkBandWidth, node1, node2):
    i = node2
    while(parent[i] != -1):
        linkBandWidth[(i,parent[i])] -= reqLinkBandWidth
        linkBandWidth[(parent[i],i)] -= reqLinkBandWidth
        i = parent[i]

def countIntermidateLinks(parent,node1,node2):
    i = node2
    ans = 0
    while(parent[i] != -1):
        ans += 1
        i = parent[i]
    return ans

# this function find the shortest path between two nodes which satisfy the bandwidth constraint
def findShortestPath(node1,node2,graph,linkBandWidth,reqLinkBandWidth,
                     subsRank,nodeLoc,linkEmbedding, maxVneDelay):
    log.info("KK Find shrotest path graph")
    #print(node1,node2,graph,linkBandWidth,reqLinkBandWidth,subsRank,nodeLoc,linkEmbedding, maxVneDelay)
    s = set()
    arr = list()
    parent = dict()
    dist = dict()
    for i in graph:
        arr.append(i)
        parent[i] = -1
        dist[i] = float('inf')
    dist[node1] = 0
    linkBandWidthTemp = _copy(linkBandWidth)
    while(arr):
        mn = minDistance(arr,dist)
        temp = arr[mn]
        arr = remove(arr,mn)
        for i in graph[temp]:
            if((dist[temp]+euclideanDistanceCal.getDistanceBetweenTwoNodes(temp,i,nodeLoc)<dist[i]) and (i not in s) and (linkBandWidthTemp[(i,temp)] >= reqLinkBandWidth)):
                dist[i] = dist[temp]+euclideanDistanceCal.getDistanceBetweenTwoNodes(temp,i,nodeLoc)
                parent[i] = temp
    if(parent[node2] != -1):
        if (parent[node2] != -1 and (countIntermidateLinks(parent, node1,
                                                           node2) <=
                                     maxVneDelay or True)):
            # updateLinkBandWidth(linkBandWidth, parent, reqLinkBandWidth, node1,
            #                     node2)
            linkEmbedding.append([parent, node1, node2])
            return True
    return False


def printEmbedding(vneEmbedding):
    '''
        @param : vneEmbedding is the dictionary containing the mapping of each Virtual node to the Substrate node
    '''
    if(vneEmbedding == -1):
        return
    for i in vneEmbedding:
        log.info('Virtual node #{0} is mapped to Substrate node #{1}'.format(i,vneEmbedding[i]))



def printRank(rank):
    '''
        @param : rank is the dictionary returned by calling nodeRankCal.calRank
    '''
    for i in rank:
        log.info('The rank of node #{0} is #{1}'.format(i,rank[i]['rank']))

def printLinkEmbedding(linkEmbedding):
    if(linkEmbedding == -1):
        return
    vne_link_dict = {}
    for i in linkEmbedding:
        log.info("link between virtual node #{0} #{1}".format(i[-2],i[-1]))
        log.info("the actual link Connection between substrate node #{0} #{1}".format(i[-4],i[-3]))
        alink = (i[-2],i[-1])
        node2 = i[-3]
        parent = i[0]
        vne_emb_link = []
        while(parent[node2] != -1):
            log.info("#{0} <-- #{1}".format(parent[node2],node2))
            vne_emb_link.append((parent[node2],node2))
            node2 = parent[node2]
        vne_link_dict[alink] = vne_emb_link
    return vne_link_dict

def calculate_vne_crb(vne_crb, vne_bandwidth, map_dict): # used for cost calculation ###
    cost = 0
    node_cost =0
    edge_cost=0
    for node in vne_crb:
        node_cost += vne_crb[node]
    for node in map_dict:
        # for v_node in node:
        #     node_cost += vne_crb[v_node]
        # sub_cost = vne_bandwidth[node]
        edge_cost += vne_bandwidth[node] * len(map_dict[node])
    return node_cost+edge_cost

    

def update_sn_crb(node_crb, vne_crb, map_dict):
    try:
        for node in map_dict:
            node_crb[map_dict[node]] -= vne_crb[node]
    except Exception as err:
        print (err)
        pass

def update_sn_bandwidth(node_bandwidth, vne_bandwidth, map_dict):

    try:
        for vn_link in map_dict:
            for n_link in map_dict[vn_link]:
                node_bandwidth[n_link] -= vne_bandwidth[vn_link]
                node_bandwidth[n_link[::-1]] -= vne_bandwidth[vn_link]
    except Exception as err:
        print (err)
        pass

def rankingMapping(graph, nodeLoc, linkBandWidth, nodeCRB,vneRequest,vneLoc,
                   vneLinkBandWidth, vneCRB, vneLR, vneDelay, page_rank):
    log.info("this is substrate network",graph)
    log.info("this is substrate network location",nodeLoc)
    log.info("this is substrate network linkBandWidth",linkBandWidth)
    log.info("this is substrate network CRB",nodeCRB)
    # subsRank = pageRank.calRank(graph, nodeLoc, linkBandWidth, nodeCRB)
    # log.info("this is substrate network rank")
    # #printRank(subsRank)
    log.info("this is vne",vneRequest)
    log.info("this is vne location",vneLoc)
    log.info("this is vne linkBandWidth",vneLinkBandWidth)
    log.info("this is vneCRB",vneCRB)
    log.info("this is vneLR", vneLR)
    log.info("this is vneDelay", vneDelay)
    if page_rank:
        return page_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay)
    else:
        return node_rank_mapping(graph, nodeLoc, linkBandWidth,
                                nodeCRB,vneRequest, vneLoc, vneLinkBandWidth,
                                 vneCRB, vneLR, vneDelay)

def page_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay):
    log.info("\nGoogle PageRank used to calculate Ranking")
    log.info("-" * 30)
    subsRank = pageRank.calRank(graph, nodeLoc, linkBandWidth, nodeCRB, delay=1)
    vneRank = pageRank.calRank(vneRequest, vneLoc, vneLinkBandWidth, vneCRB,
                               delay=vneDelay)
    # #printRank(vneRank)
    subsSort = nodeSort(subsRank)
    log.info("Google PageRank :Sorted SN nodes after rank {} ".format(subsSort))
    vneSort = nodeSort(vneRank)
    log.info("Google PageRank :Sorted VNR nodes after rank {} ".format(vneSort))
    vneEmbedding = dict()
    for i in vneRequest:
        vneEmbedding[i] = -1
    # log.info("\nthis is substrate(Physical) network rank after Virtual "
    #       "network embedding")
    log.info("\nthis is substrate network rank : Google Page Rank")
    log.info("-" * 30)
    printRank(subsRank)
    log.info("\nthis is vne Rank : Google Page Rank")
    log.info("-" * 30)
    printRank(vneRank)
    flag = True
    nodeCRBTemp = _copy(nodeCRB)
    vneCRBTemp = _copy(vneCRB)
    j = len(vneSort) - 1

    # this part will map the nodes
    while (j > -1):
        i = len(subsSort) - 1
        while (True):
            #print(subsSort[i], vneSort[j])
            if ((nodeCRBTemp[subsSort[i]] >= vneCRBTemp[vneSort[j]]) and (
                eucDis(nodeLoc[subsSort[i]], vneLoc[vneSort[j]]) <=30)):
                # <= vneLR[vneSort[j]] or True )):  #<=30)):
                vneEmbedding[vneSort[j]] = subsSort[i]
                nodeCRBTemp[subsSort[i]] -= vneCRBTemp[vneSort[j]]
                subsSort = remove(subsSort, i)

                break
            i -= 1
            if (i == -1):
                flag = False
                break
        j -= 1
        if ((not flag) or (len(subsSort) == 0 and j > -1)):
            break

    # this part will map the edges
    if (flag):
        edgesToBeMapped = set()
        for i in vneRequest:
            for j in vneRequest[i]:
                if ((i, j) in edgesToBeMapped or (j, i) in edgesToBeMapped):
                    continue
                edgesToBeMapped.add((i, j))
        linkEmbedding = list()
        for i in edgesToBeMapped:
            node1 = vneEmbedding[i[0]]
            node2 = vneEmbedding[i[1]]
            reqLinkBandWidth = vneLinkBandWidth[i]
            if (not findShortestPath(node1, node2, graph, linkBandWidth,
                                     reqLinkBandWidth, subsRank, nodeLoc,
                                     linkEmbedding, vneDelay[i])):
                return [-1, -1]
            linkEmbedding[-1].append(i[0])
            linkEmbedding[-1].append(i[1])
        nodeCRB = nodeCRBTemp
        # i also need to return link embedding
        return [vneEmbedding, linkEmbedding]
    return -1

def node_rank_mapping(graph, nodeLoc, linkBandWidth, nodeCRB,
                      vneRequest, vneLoc, vneLinkBandWidth, vneCRB, vneLR,
                      vneDelay):
    log.info("\nNodeRank used to calculate Ranking")
    log.info("-"*30)
    subsRank = nodeRankCal.calRank(graph, nodeLoc, linkBandWidth, nodeCRB,
                                   delay=1)
    vneRank = nodeRankCal.calRank(vneRequest,vneLoc, vneLinkBandWidth, vneCRB, delay=vneDelay)
    # #printRank(vneRank)
    subsSort = nodeSort(subsRank)
    log.info("Direct rank :Sorted SN nodes after rank {} ".format(subsSort))
    vneSort = nodeSort(vneRank)
    log.info("Direct rank: Sorted VNR nodes after rank {} ".format(vneSort))
    vneEmbedding = dict()
    for i in vneRequest:
        vneEmbedding[i] = -1
    # log.info("\nthis is substrate(Physical) network rank after Virtual "
    #       "network embedding")
    log.info("\nthis is substrate network rank: Direct Method")
    log.info("-" * 30)
    printRank(subsRank)
    log.info("\nthis is vne Rank:  Direct Method")
    log.info("-" * 30)
    printRank(vneRank)
    flag = True
    nodeCRBTemp = _copy(nodeCRB)
    vneCRBTemp = _copy(vneCRB)
    j = len(vneSort) - 1
    # this part will map the nodes######################################################################33
    while (j > -1):
        i = len(subsSort) - 1
        while (True):
            if ((nodeCRBTemp[subsSort[i]] >= vneCRBTemp[vneSort[j]]) and (
                eucDis(nodeLoc[subsSort[i]], vneLoc[vneSort[j]]) <= vneLR[
                vneSort[j]] or True)):
                vneEmbedding[vneSort[j]] = subsSort[i]
                nodeCRBTemp[subsSort[i]] -= vneCRBTemp[vneSort[j]]
                subsSort = remove(subsSort, i)
                break
            i -= 1
            if (i == -1):
                flag = False
                break
        j -= 1
        if ((not flag) or (len(subsSort) == 0 and j > -1)):
            break

    # this part will map the edges
    if (flag):
        edgesToBeMapped = set()
        for i in vneRequest:
            for j in vneRequest[i]:
                if ((i, j) in edgesToBeMapped or (j, i) in edgesToBeMapped):
                    continue
                edgesToBeMapped.add((i, j))
        linkEmbedding = list()
        for i in edgesToBeMapped:
            node1 = vneEmbedding[i[0]]
            node2 = vneEmbedding[i[1]]
            reqLinkBandWidth = vneLinkBandWidth[i]
            if (not findShortestPath(node1, node2, graph, linkBandWidth,
                                     reqLinkBandWidth, subsRank, nodeLoc,
                                     linkEmbedding, vneDelay[i])):
                return [-1, -1]
            linkEmbedding[-1].append(i[0])
            linkEmbedding[-1].append(i[1])
        nodeCRB = nodeCRBTemp
        # i also need to return link embedding
        return [vneEmbedding, linkEmbedding]
    return -1

# function to generate node location
def generatenodeLoc(network, original_net):
    networkLoc = dict()
    for i in network:
        # networkLoc[i] = (random.randint(0,100),random.randint(0,100))
        x, y = original_net.node_pos[i-1]
        networkLoc[i] = (x, y)
    return networkLoc

# function to generate linkBandWidth
def generatelinkBandWidth(network,flag, original_net):
    linkBandWidth = dict()
    for i in network:
        for j in network[i]:
            if((j,i) in linkBandWidth):
                linkBandWidth[(i,j)] = linkBandWidth[(j,i)]
            else:
                if(not flag):
                    linkBandWidth[(i,j)] = original_net.edge_weights[(str(i-1),str(j-1))] # for SN
                else:
                    linkBandWidth[(i,j)] = original_net.edge_weights[(str(i-1),str(j-1))] # for VNR
    return linkBandWidth

# function to generate CRB
def generateCRB(network,flag, original_net):
    networkCRB = dict()
    for i in network:
        if(not flag):
            networkCRB[i] = original_net.node_weights[i-1] # for SN
        else:
            networkCRB[i] = original_net.node_weights[i-1] # for VNR
    return networkCRB


# this function will calculate the revenue of vne
def calculateRevenue(vneList, crb_unit_cost, bwd_unit_cost):
    for vneContainer in vneList:
        bandWidth = vneContainer[2]
        crb = vneContainer[3]
        bandWidthSum = 0
        crbSum = 0
        for i in crb:
            crbSum += crb[i]
        for i in bandWidth:
            bandWidthSum += bandWidth[i]
        bandWidthSum = bandWidthSum//2
        revenue = (bandWidthSum * 1 * bwd_unit_cost) + (crbSum * 1 *
                                                        crb_unit_cost)   # maintaing constant factor as 1 but as per paper it is 05
        # revenue = (bandWidthSum * 0.5) + crbSum
        vneContainer.append(int(revenue))


# this function will sort the vneList according to revenue in ascending order
def sortAccordingToRevenue(vneList):
    for i in range(len(vneList)):
        for j in range(len(vneList)-1):
            if(vneList[j][-1]>vneList[j+1][-1]):
                temp = vneList[j]
                vneList[j] = vneList[j+1]
                vneList[j+1] = temp

def generateDelay(vneRequest, original_net):
    delay = dict()
    for i in vneRequest:
        for j in vneRequest[i]:
            if((j,i) in delay):
                delay[(i,j)] = delay[(j,i)]
            else:
                delay[(i,j)] = original_net.delay[(str(i-1),str(j-1))]
    return delay

def BFS(src, dest, v, pred, dist, weight, vnr):
    queue = []
    visited = []
    visited = [False for i in range(v+1)]
    for i in range(v+1):
        dist[i] = 1000000
        pred[i] = -1
    visited[int(src)] = True
    dist[int(src)] = 0
    queue.append(src)
    while len(queue) != 0:
        u = queue[0]
        queue.pop(0)
        for i in vnr[int(u)]:
            if visited[int(i)] == False :
                visited[int(i)] = True
                dist[int(i)] = dist[int(u)] + 1
                pred[int(i)] = u
                queue.append(i)
                if int(i) == int(dest):
                    return True
    return False

def findShortest(s, dest, weight, vnr):
    v = len(vnr.keys())
    pred = [0 for i in range(v+1)]
    dist = [0 for i in range(v+1)]
    ls = []
    if BFS(s, dest, v, pred, dist, weight,vnr) == False:
        return ls
    path = []
    crawl = dest
    crawl = dest
    path.append(crawl)

    while pred[int(crawl)] != -1:
        path.append(pred[int(crawl)])
        crawl = pred[int(crawl)]

    for i in range(len(path) - 1, -1, -1):
        ls.append(path[i])

    return ls
    
def findAvgPathLength(vneRequest):
    cnt = 0            
    for node1 in vneRequest:
        for node2 in vneRequest:
            if(node1 != node2):
                path = findShortest(str(node1), str(node2), 0, vneRequest)
                cnt += len(path)-1
    total_nodes = len(vneRequest.keys())
    cnt /= (total_nodes)*(total_nodes-1)
    return cnt

def embed_rank_mapping(start_time, sn, snLoc, snLinkBandWidth, snCRB, vneList,
                       page_rank=True):  # embedding
    accepted = []
    pre_sub_edgecost=sum(snLinkBandWidth.values())//2
    pre_sub_nodecost=sum(snCRB.values())
    copy_edge = copy.deepcopy(snLinkBandWidth)
    copy_node = copy.deepcopy(snCRB)
    total_vne_cost = 0
    total_vne_revenue = 0
    total_vne = len(vneList)
    failed_vne = 0
    path_cnt=0
    vl_cnt=0
    total_vnr_nodes = 0
    total_vnr_links = 0
    avg_path_length = 0
    avg_path_length_modified = 0
    for vneContainer in vneList:
        vneRequest = vneContainer[0]
        vneLoc = vneContainer[1]
        vnelinkBandWidth = vneContainer[2]
        vneCRB = vneContainer[3]
        vneLR = vneContainer[4]
        vneDelay = vneContainer[5]
        total_vnr_nodes += len(vneRequest)
        for i in vneRequest.values():
            total_vnr_links += len(i)
        # total_vne_revenue += vneContainer[-2]
        log.info(f"crb: {sum(vnelinkBandWidth.values())//2} bw: {sum(vneCRB.values())}")
        log.info("\nEmbedding for virtual network request: %s of revenue: %s$"%
              (vneContainer[ -1], vneContainer[-2]))
        log.info("-" * 60)
        tmp = rankingMapping(sn, snLoc, snLinkBandWidth, snCRB, vneRequest, vneLoc,
                        vnelinkBandWidth, vneCRB, vneLR, vneDelay, page_rank)
        if tmp==-1:
            tmp = [-1]
        embeding_out = [vneContainer[-1], tmp]
        log.info('\nEmbedding details of vne %s' % embeding_out[0])
        log.info("-" * 30)
        # log.infosnLinkBandWidth
        # log.infovnelinkBandWidth
        if embeding_out[1][0] == -1:
            failed_vne += 1
            log.info('Error - Embedding is skipped as No shortest path found')
        else:
            printEmbedding(embeding_out[1][0])
            update_sn_crb(snCRB, vneCRB, embeding_out[1][0])

            link_map_dict = printLinkEmbedding(embeding_out[1][1])
            update_sn_bandwidth(snLinkBandWidth, vnelinkBandWidth,
                                link_map_dict)
            _ncost = calculate_vne_crb(vneCRB, vnelinkBandWidth, link_map_dict)
            total_vne_cost += _ncost
            path_cnt_modified = 0
            for node in link_map_dict:
                path_cnt +=len(link_map_dict[node])
                path_cnt_modified += (len(link_map_dict[node]) - 1)
                vl_cnt += 1
            avg_path_length += findAvgPathLength(vneRequest)
            avg_path_length_modified +=((path_cnt_modified) / (len(vnelinkBandWidth)//2))
            accepted.append(vneContainer)
            log.info("\ncost incurred for embedding vne %s is %s$" % (vneContainer[
                                                                    -1], _ncost))
            log.info("-" * 30)
    for container in accepted:
        total_vne_revenue += container[-2]
    if len(accepted) != 0:
        avg_path_length_modified /= len(accepted)    
    post_sub_edgecost =0
    post_sub_nodecost=0
    utilized_nodes=0
    utilized_links=0
    average_node_utilization = 0
    average_edge_utilization = 0
    for edge in snLinkBandWidth:
        post_sub_edgecost += snLinkBandWidth[edge]
        if snLinkBandWidth[edge]!=copy_edge[edge]:
            utilized_links += 1
            average_edge_utilization+=((copy_edge[edge]-snLinkBandWidth[edge])/copy_edge[edge])
            logging.info(f"The edge utilization of substrate edge {edge} is {((copy_edge[edge]-snLinkBandWidth[edge])/copy_edge[edge])*100:0.4f}")
    post_sub_edgecost //= 2
    if utilized_links != 0:
        average_edge_utilization = average_edge_utilization / 2
        average_edge_utilization /= (utilized_links//2)
    for node in snCRB:
        post_sub_nodecost += snCRB[node]
        if snCRB[node] != copy_node[node]:
            utilized_nodes += 1
            average_node_utilization+=((copy_node[node]-snCRB[node])/copy_node[node])
            logging.info(f"The node utilization of substrate node {edge} is {((copy_node[node]-snCRB[node])/copy_node[node])*100:0.4f}")
    if utilized_nodes != 0:    
        average_node_utilization /= utilized_nodes
    no_cost = pre_sub_nodecost-post_sub_nodecost
    ed_cost = pre_sub_edgecost-post_sub_edgecost
    if((total_vne-failed_vne)!=0): #added if
        avg_path_length /= (total_vne-failed_vne)

    end_time = datetime.now().time()
    duration = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)    
    
    embedding_ratio = (float(total_vne - failed_vne) / float(total_vne)) * 100
    log.info("\n\n\n")
    if page_rank:
        log.info("\t\tSummary (Stble google PageRank):")
    else:
        log.info("\t\tSummary (Direct Method NodeRank):")
    log.info("*" * 100)
    log.info(f"The revenue is {total_vne_revenue} and total cost is {total_vne_cost}")
    if total_vne_cost == 0:
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
        return output_dict
    log.info(f"The revenue to cost ratio is {(total_vne_revenue/total_vne_cost)*100:.4f}%")
    log.info(f"Total {total_vne-failed_vne} requests are embedded out of {total_vne}")
    log.info(f"Embedding ratio is {((total_vne-failed_vne)/total_vne )*100:.4f}%\n")
    log.info(f"Substrate links utilized are {utilized_links//2} out of {len(snLinkBandWidth)//2}")
    log.info(f"Substrate nodes utilized are {utilized_nodes} out of {len(snCRB)}")
    # log.info(f"Average node utilization is {(utilized_nodes/len(snCRB))*100:0.4f}")
    # log.info(f"Average link utilization is {(utilized_links/len(snLinkBandWidth))*100:0.4f}\n")
    log.info(f"\t\tAverage node CRB utilization is {average_node_utilization*100:0.4f}")
    log.info(f"\t\tAverage link BW utilization is {average_edge_utilization*100:0.4f}\n")
    log.info(f"Substrate before embedding CRB: {pre_sub_nodecost} BW: {pre_sub_edgecost} total: {pre_sub_nodecost+pre_sub_edgecost}")
    log.info(f"Substrate after embedding CRB: {post_sub_nodecost} BW: {post_sub_edgecost} total: {post_sub_nodecost+post_sub_edgecost}")
    log.info(f"Substrate consumed CRB: {no_cost} BW: {ed_cost} total: {no_cost+ed_cost}\n")
    log.info(f"Average Path Length {avg_path_length_modified:.4f}\n")
    # log.info(f"Average BW utilization {(ed_cost/pre_sub_edgecost)*100:.4f}%")
    # log.info(f"Average CRB utilization {(no_cost/pre_sub_nodecost)*100:.4f}%")
    log.info(f"Average Execution time {duration/total_vne}")
    
    log.info("#"*100)
    if page_rank:
        log.info("\n\n\n\n\n\n\n\n")

    output_dict = {
        "revenue": total_vne_revenue,
        "total_cost" : total_vne_cost,
        "accepted" : total_vne-failed_vne,
        "total_request": total_vne,
        "pre_resource": pre_sub_nodecost+pre_sub_edgecost,
        "post_resource": post_sub_nodecost+post_sub_edgecost,
        "avg_bw": (average_edge_utilization)*100,
        "avg_crb": (average_node_utilization)*100,
        "avg_link": ((utilized_links/len(snLinkBandWidth))/2)*100,  #
        "No_of_Links_used": (utilized_links//2),  #avg_link in %
        "avg_node": (utilized_nodes/len(snCRB))*100,
        "No_of_Nodes_used": (utilized_nodes),   # avg_node in %
        "avg_path": avg_path_length_modified,
        "avg_exec": (duration),
        "total_nodes": total_vnr_nodes,
        "total_links": total_vnr_links//2,
    }
    return output_dict

def generateReqDelay(requests):
    for request in requests:
        delay = dict()
        for i in request:
            for j in request[i]:
                if((j,i) in delay):
                    delay[(i,j)] = delay[(j,i)]
                else:
                    delay[(i,j)] = random.randint(1,4)
        return delay

# This is the main function to be called to get the embedding
def calling(start_time, sn, vneRequests, substrate, vne_list):
    '''
        @param : sn -> this is the substrate graph {must be in the from of dictionary}
        @param : vneRequests -> this is the list of vneRequest where each vneRequest is the vne graph {must be in the form of dictionary}
    '''
    cost_per_unit_crb = 1
    cost_per_unit_bandwidth = 1
    log.info("this is all the inputs and their values\n")
    snLoc = generatenodeLoc(sn, substrate)
    snLinkBandWidth = generatelinkBandWidth(sn,False, substrate)
    snCRB = generateCRB(sn,False, substrate)

    # snLinkBandWidth = {(1,2):5,(2,1):5,(2,5):6,(5,2):6,(5,4):10,(4,5):10,(4,3):4,(3,4):4,(1,3):4,(3,1):4,(3,5):10,(5,3):10}
    # snCRB = {1:5,2:5,3:15,4:16,5:15}
    vneEmbeddings = list()
    vneList = list()
    for i in range(len(vne_list)):
    # for vneRequest in vneRequests:
        vneRequest = vneRequests[i]
        vneLoc = generatenodeLoc(vneRequest, vne_list[i])
        vnelinkBandWidth = generatelinkBandWidth(vneRequest,True, vne_list[i])
        vneCRB = generateCRB(vneRequest,True, vne_list[i])
        # vnelinkBandWidth = {(1,2):10,(2,1):10}
        # vneCRB = {1:15,2:16}
        vneLR = generateLR(vneRequest)
        vneDelay = generateDelay(vneRequest, vne_list[i])
        # vneList.append([vneRequest,vneLoc,vnelinkBandWidth,vneCRB,vneLR,vneDelay])
        vneList.append([vneRequest,vneLoc,vnelinkBandWidth,vneCRB,vneLR,vneDelay])
    calculateRevenue(vneList, cost_per_unit_crb, cost_per_unit_bandwidth)
    for i in range(len(vneList)):
        vneList[i].append(i)
    sortAccordingToRevenue(vneList)
    _sn = copy.deepcopy(sn)
    _snLoc = copy.deepcopy(snLoc)
    _snLinkBandWidth = copy.deepcopy(snLinkBandWidth)
    _snCRB = copy.deepcopy(snCRB)
    _vneList = copy.deepcopy(vneList)
    start_time = datetime.now().time()
    output1 = embed_rank_mapping(start_time, sn, snLoc, snLinkBandWidth, snCRB, vneList,
                       page_rank=True)
    start_time = datetime.now().time()
    output2 = embed_rank_mapping(start_time, _sn, _snLoc, _snLinkBandWidth, _snCRB, _vneList,
                       page_rank=False)
    return (output1, output2)


def generate_sn_rank(sn):
    snLoc = generatenodeLoc(sn)
    snLinkBandWidth = generatelinkBandWidth(sn, False)
    snCRB = generateCRB(sn, False)



def embedded_map(sn, vneRequests):
    log.info("this is all the inputs and their values\n")


if __name__=="__main__":
    # sn = {1:[2,3],2:[1,5],3:[1,4,5],4:[3,5],5:[2,3,4]}
    # vne = [{1:[2], 2:[1]}]
    sn = {2: [4, 1], 4: [2, 1, 5], 5: [4, 3], 3: [5, 1], 1: [2, 3, 4]}
    vne = [{1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3], 3: [1, 2], 2: [1, 3]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]},
           {1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]}
           ,{1: [2, 3, 4], 3: [1, 2, 4], 4: [1, 2, 3], 2: [1, 3, 4]}]

    temp = calling(sn,vne)
    # log.info("Here is all the embedding if found any")
    # for i in temp:
    #     log.info('embedding for vne',i[0])
    #     if(i[1] == -1):
    #         log.info("No embedding found")
    #         continue
    #     #printEmbedding(i[1][0])
    #     #printLinkEmbedding(i[1][1])



















