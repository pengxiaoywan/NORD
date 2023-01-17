import math
import logging
log = logging.getLogger(__name__)

class EigenvectorCentrality(object):
  def __init__(self, network):
    self.network = network

  def get_transition_matrix(self):
    matrix = [[0 for i in range(len(self.network))] for j in range(len(self.network))]
    for i in self.network:
      for j in self.network[i]:
        matrix[i - 1][j - 1] = 1
    # for i in matrix:
    #   log.info i,
    #   log.info
    print("KK matrix is",matrix)
    return matrix

  def get_identity_matrix(self):  # Make sure I matrix must be updated for each iteration
    imatrix = [[1] for i in range(len(self.network))]
    print("KK I matrix is",imatrix)
    return imatrix

  @staticmethod
  def matrix_multiplication(m1, m2):
    return [[sum(x * y for x, y in zip(m1_r, m2_c)) for m2_c in zip(*m2)] for
            m1_r in m1]

  def get_normalized_eigen_matrix(self):
    m1 = self.get_transition_matrix()
    m2 = self.get_identity_matrix()
    eigen_matrix = self.matrix_multiplication(m1, m2)
    norm_matrix = math.sqrt(sum(value[0] ** 2 for value in eigen_matrix))
    imatrix = [[float(_ei[0])/float(norm_matrix)] for _ei in eigen_matrix]
    imatrix = [[round((x[0]), 3)] for x in imatrix]
    print("KK I matrix is inside",imatrix) # Matching with First iterration values
    return imatrix

  def eigenvector_centrality(self, max_iter=3):
    if len(self.network) == 0:
      raise Exception("cannot compute centrality for the null graph")
    m2 = self.get_normalized_eigen_matrix()
    print ("KK Value M2",m2)
    for i in range(max_iter):
      m1 = self.get_transition_matrix()
      eigen_matrix = self.matrix_multiplication(m1, m2)
      norm_matrix = math.sqrt(sum(value[0] ** 2 for value in eigen_matrix))
      imatrix = [[float(_ei[0]) / float(norm_matrix)] for _ei in eigen_matrix]
      m2 = [[round((x[0]), 3)] for x in imatrix]
      #print("KK I matrix is inside2", imatrix) #Not matching
    log.info( 'Eigen vector_centrality: %s' % m2)
    return m2