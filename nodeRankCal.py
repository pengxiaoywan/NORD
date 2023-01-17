''' Given a graph in the form of dictionary
    we calculate the rank of each node and return that in the form
    dictionary'''
import math
import euclideanDistanceCal
import logging
log = logging.getLogger(__name__)

def getDegreeOfNode(graph,node):
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
    far1 = nodeRank[node1]['farness']
    far2 = nodeRank[node2]['farness']
    d1 = nodeRank[node1]['degree']
    d2 = nodeRank[node2]['degree']
    li = (far1/d1)+(far2/d2)
    return li




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
        nodeRank[i]['farness'] = getFarness(i, allPairShortestPath[i - 1])
        if (nodeRank[i]['farness'] < 1):  # Handling division by zero error while calculating "closeness"
            nodeRank[i]['farness'] = 1
        nodeRank[i]['closeness'] = 1 / nodeRank[i]['farness']
        nodeRank[i]['rank'] = -1
    for i in nodeRank:
        # added below 2 lines
        nodeRank[i]['li'] = getLinkInterferenceOfANode(i, nodeRank)


def calRB(rb, nodeRank, nodeCRB):
    for i in rb:
        rb[i] = nodeCRB[i] * nodeRank[i]['strength']
        temp = 0
        for j in nodeRank[i]['li'].values():
            temp += j
        rb[i] *= temp



def getNOV(rb,nodeRank, delay):
    try:
        novMatrix = [[-1 for i in range(len(nodeRank))] for j in range(len(nodeRank))]

        Delay = delay #if not virtual_nt else
        for i in range(len(novMatrix)):
            for j in range(len(novMatrix)):
                if(i == j):
                    novMatrix[i][j] = 0
                    continue
                temp = rb[i+1]*rb[j+1]*1 # 1= alpha
                if delay ==1:
                    den = (nodeRank[i+1]['distance'][j+1]**2) * Delay
                elif (i + 1, j + 1) in Delay:
                    den = (nodeRank[i + 1]['distance'][j + 1] ** 2) * (Delay[(i + 1, j + 1)]**2)
                else:
                    den = None
                novMatrix[i][j] = temp/den if den else -1
        return novMatrix
    except Exception as err:
        log.info(err)


def getNov(novMatrix):
    nov = dict()
    for i in range(len(novMatrix)):
        temp = 0
        for j in novMatrix[i]:
            temp += j
        nov[i+1] = temp
    return nov


def getRank(nodeRank,rb,nov):
    novNorm = 0
    rbNorm = 0
    for i in rb:
        rbNorm += rb[i]**2
    for i in nov:
        novNorm += nov[i]**2
    rbNorm = math.sqrt(rbNorm)
    novNorm = math.sqrt(novNorm)
    for i in nodeRank:
        nodeRank[i]['rank'] = (1*(rb[i]/rbNorm))+(1*(nov[i]/novNorm)) # .4 and .3



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

    getValueOfAllAttributes(nodeRank,graph,nodeLoc,linkBandWidth,nodeCRB)

    calRB(rb,nodeRank,nodeCRB)

    novMatrix = getNOV(rb,nodeRank,delay)

    nov = getNov(novMatrix)

    getRank(nodeRank,rb,nov)

    return nodeRank




