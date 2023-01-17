''' Given a graph in the form of dictionary
    we calculate the rank of each node and return that in the form
    dictionary'''
from __future__ import division
import math
from platform import node
import euclideanDistanceCal
import logging
log = logging.getLogger(__name__)


def getDegreeOfNode(graph,node):
    if len(graph[node]) == 0:
        print
    return len(graph[node])


def getStrengthOfNode(graph,linkBandWidth,node):
    ans = 0
    for i in graph[node]:
        ans += linkBandWidth[(node,i)]
    return ans



def getDistanceBetweenAllNodes(graph,nodeLoc):
    return euclideanDistanceCal.euclideanDistance(graph,nodeLoc)




def getFarness(node, distanceArray):

    farness = 0
    for i in distanceArray:
        farness += i
    return farness




def getLinkInterferenceOfALink(node1,node2,nodeRank):
    try:
        far1 = nodeRank[node1]['farness']
        far2 = nodeRank[node2]['farness']
        d1 = nodeRank[node1]['degree']
        d2 = nodeRank[node2]['degree']
        li = (far1/d1)+(far2/d2)
        return li
    except Exception as err:
        print (err)


def getDistanceInFormOfDictionary(distanceArray, node):
    distance = dict()
    for i in range(len(distanceArray)):
        if(i+1 == node):
            continue
        distance[i+1] = distanceArray[i]
    return distance



def getLinkInterferenceOfANode(node,nodeRank):
    li = dict()
    for i in nodeRank:
        if(i == node):
            continue
        li[i] = getLinkInterferenceOfALink(node,i,nodeRank)
    return li



def getValueOfAllAttributes(nodeRank,graph,nodeLoc,linkBandWidth,nodeCRB):
    allPairShortestPath = getDistanceBetweenAllNodes(graph,nodeLoc)
    for i in nodeRank:
        nodeRank[i]['degree'] = getDegreeOfNode(graph,i)
        nodeRank[i]['strength'] = getStrengthOfNode(graph,linkBandWidth,i)
        nodeRank[i]['distance'] = getDistanceInFormOfDictionary(allPairShortestPath[i-1],i)
        nodeRank[i]['farness'] = getFarness(i, allPairShortestPath[i-1])
        if(nodeRank[i]['farness'] < 1):     # Handling division by zero error while calculating "closeness"
            nodeRank[i]['farness'] = 1
        nodeRank[i]['closeness'] = 1/nodeRank[i]['farness']
        nodeRank[i]['rank'] = -1
    for i in nodeRank:
        # added below 2 lines
        nodeRank[i]['li'] = getLinkInterferenceOfANode(i,nodeRank)


def calRB(rb, nodeRank, nodeCRB):
    try:
        for i in rb:
            rb[i] = nodeCRB[i] * nodeRank[i]['strength']
            temp = 0
            for j in nodeRank[i]['li'].values():
                temp += j
            rb[i] *= temp
    except Exception as err:
        print (err)



def getNOV(rb,nodeRank, delay):
    novMatrix = [[-1 for i in range(len(nodeRank))] for j in range(len(nodeRank))]
    try:
        Delay = delay
        for i in range(len(novMatrix)):
            for j in range(len(novMatrix)):
                if(i == j):
                    novMatrix[i][j] = 0
                    continue
                temp = rb[i+1]*rb[j+1]*1 # 1 is alpha
                if delay == 1:
                    den = (nodeRank[i + 1]['distance'][j + 1] ** 2) * Delay
                elif (i + 1, j + 1) in Delay:
                    den = (nodeRank[i + 1]['distance'][j + 1] ** 2) * (Delay[(i + 1, j + 1)]**2)
                else:
                    den = None
                novMatrix[i][j] = temp/den if den else -1
    except Exception as err:
        log.info(err)
    return novMatrix


def getNov(novMatrix):
    nov = dict()
    for i in range(len(novMatrix)):
        temp = 0
        for j in novMatrix[i]:
            temp += j
        nov[i+1] = temp
    return nov

def getTransitionMatrix(graph):
    matrix = [[0 for i in range(len(graph))] for j in range(len(graph))]
    for i in graph:
        for j in graph[i]:
            matrix[i-1][j-1] = 1
    return matrix

def mulMatrixByNum(num,matrix):
    temp = list()
    for i in matrix:
        temp.append(i*num)
    return temp

def mulMatrix(M,matrix):
    temp = list()
    for i in range(len(matrix)):
        ans = 0
        count = 0
        while(count<len(matrix)):
            ans += M[i][count] * matrix[count]
            count += 1
        temp.append(ans)
    return temp

def addMatrix(matrix1,matrix2):
    temp = list()
    count = 0
    while(count<len(matrix1)):
        ans = matrix1[count] + matrix2[count]
        count += 1
        temp.append(ans)
    return temp

def calW_old(matrix1,matrix2):
    m1 = 0
    m2 = 0
    for i in range(len(matrix1)):
        m1 += abs(matrix1[i])
        m2 += abs(matrix2[i])
    return m2-m1
def calW_new(matrix1,matrix2):
    mat_diff_arr = []
    for i in range(len(matrix1)):
        mat_diff_arr.append((matrix1[i] - matrix2[i]))
    sum = 0
    for _arr in mat_diff_arr:
        sum += (_arr*_arr)
    n_value = math.sqrt(sum)
    if n_value < 0.000001:
        n_value=1
    final_vlaue = max([elem/n_value for elem in mat_diff_arr])
    return final_vlaue

def calW(matrix1,matrix2):
    mat_diff_arr = []
    for i in range(len(matrix1)):
        mat_diff_arr.append((matrix1[i]-matrix2[i]))
    matrix_value = max(mat_diff_arr)
    return matrix_value

def getRank(nodeRank,rb,nov,graph, matrix):
    rbNormalized = list()
    initialRank = list()
    denomrb = 0
    denomNov = 0

    for i in rb:
        denomrb += rb[i]**2
    denomrb = math.sqrt(denomrb)

    for i in nov:
        denomNov += nov[i]**2
    denomNov = math.sqrt(denomNov)

    for i in rb:# rb normalized
        rbNormalized.append(rb[i]/denomrb)

    for i in nov:
        initialRank.append(nov[i]/denomNov) # Nov normalized initialrank=[Nov%1,NOV%2] i.e normaized NOV

    M = getTransitionMatrix(graph)
    d = 0.85
    k = 0
    rank = list()
    # now I need to perform matrix multiplication
    gamma = 0.00001
    w = 2#50#8
    ev_rank = {}
    for _i in range(len(matrix)):  # initialrank=[Nov%1,NOV%2] i.e normaized NOV
        sum = 0                    # EVen_rank(r_m)= 1-d*RM%(m)+d* sum[(nov(m.n))] *  NOC%m] here r_n=NOV%2 from initial rank vector
        for _j in matrix[_i]:
            sum += _j
        ev_rn = (1 - d)* rbNormalized[_i] + d * sum * initialRank[_i]
        ev_rank[_i+1] = ev_rn

    newRank_old = []
    while(w>=gamma):
        #log.info('this is newrank')
        #log.info(newRank)
        #break
        # need to clarify calW          newRank=(1-d)*(Sum(RB%1,2,3)+ d *M * R0(T0)
        if k == 0:
            newRank = addMatrix(mulMatrixByNum(0.15, rbNormalized),
                                mulMatrixByNum(0.85, (mulMatrix(M,list(ev_rank.values())))))  # change from initialrank to ev_rank.values()
            w = calW_new(newRank,list(ev_rank.values())) # change from initialrank to
            # ev_rank.values()
        else:
            newRank = addMatrix(mulMatrixByNum(0.15, rbNormalized),
                                mulMatrixByNum(0.85, (mulMatrix(M,newRank_old))))  # change from initialrank to ev_rank.values()
            w = calW_new(newRank, newRank_old)
        newRank_old = newRank
        k += 1
    count = 0
    for i in nodeRank:
        nodeRank[i]['rank'] = newRank[count]
        count += 1


# This is the method which should be called by other module to calculate
# the rank of the nodes of graph
def calRank(graph, nodeLoc, linkBandWidth, nodeCRB, delay):
    '''
        @param : graph in the form of dictionary
        @param : nodeLoc in the form of dictionary
        @param : linkBandWidth in the form of dictionary
        @param : nodeCRB in the form of dictionary
        return : dictionary which consists of each node degree, strength
                , distance, farness, closeness, li and rank
    '''
    nodeRank = dict()
    rb = dict()
    for i in graph:
        rb[i] = -1
        nodeRank[i] = {
            'degree' : -1,
            'strength' : -1,
            # distance is the dictionary which contains euclidean distance to all other node
            'distance' : dict(),
            'farness' : -1,
            'closeness' : -1,
            # same use as distance
            'li' : dict(),
            'rank' : -1,
        }
    # RB and NOV is not normalized right now
    # if needed to be done at that time
    # log.info('graph')
    # print graph
    getValueOfAllAttributes(nodeRank,graph,nodeLoc,linkBandWidth,nodeCRB)

    calRB(rb,nodeRank,nodeCRB)

    novMatrix = getNOV(rb,nodeRank, delay)
    temp_novMatrix = novMatrix[::]
    nov = getNov(novMatrix)

    getRank(nodeRank,rb,nov,graph, temp_novMatrix)

    return nodeRank




