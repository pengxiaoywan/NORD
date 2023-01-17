'''
    this module will take a graph and all the node location and
    then generate a matrix that will contain euclidean distance
    of each node to other node
'''
import math

def getDistanceBetweenTwoNodes(node1,node2,nodeLoc):
    dis = 0
    x1 = nodeLoc[node1][0]
    y1 = nodeLoc[node1][1]
    x2 = nodeLoc[node2][0]
    y2 = nodeLoc[node2][1]
    return math.sqrt((((x1-x2)**2)+((y1-y2)**2)))

# The algorithm used here is floyd warshall all pair shortest path
def euclideanDistance(graph, nodeLoc):
    # initialization part
    INF=999
    dp = [[float(INF) for i in range(len(graph))] for j in range(len(graph))]
    for i in range(len(dp)):
        dp[i][i] = 0
    for i in graph:
        for j in graph[i]:
            dp[i-1][j-1] = getDistanceBetweenTwoNodes(i,j,nodeLoc)
    # Actual algorithm implementation
    for k in range(len(graph)):
        for i in range(len(graph)):
            for j in range(len(graph)):
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k][j])
    return dp
    
    
