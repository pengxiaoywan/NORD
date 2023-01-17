import copy
import sys
import random
import math
import logging

x = False


class temp_map:
    def __init__(self, vne_list, req_no, map=[]) -> None:
        self.node_map = map
        self.node_cost = 0
        self.node_cost += sum(vne_list[req_no].node_weights.values())
        self.edge_cost = 0
        self.total_cost = sys.maxsize
        self.edge_map = []
        self.edges = []
        self.edge_weight = []
        self.path_cost = []
        self.fitness = 0


def check_location(substrate, virtual, snode, vnode, radius):
    x1, y1 = substrate.node_pos[snode]
    x2, y2 = virtual.node_pos[vnode]
    if math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1))) <= radius:
        return True
    return False


# Also check for distance constraint(location)
def node_map(substrate, virtual, req_no):
    map = [0 for x in range(virtual.nodes)]
    sorder = sorted(
        [a for a in range(substrate.nodes)],
        key=lambda x: substrate.node_weights[x],
        reverse=True,
    )  # descending order
    vorder = sorted(
        [a for a in range(virtual.nodes)],
        key=lambda x: virtual.node_weights[x],
        reverse=True,
    )
    assigned_nodes = set()
    for vnode in vorder:
        for snode in sorder:
            if (
                substrate.node_weights[snode] >= virtual.node_weights[vnode]
                and snode not in assigned_nodes # constraint for non-repeating node number
                and check_location(substrate, virtual, snode, vnode, 100) # pass radius here
            ):
                map[vnode] = snode
                substrate.node_weights[snode] -= virtual.node_weights[vnode]
                assigned_nodes.add(snode)
                break
            if snode == sorder[-1]:
                return None
    return map


def selectPaths(
    i, virtual_edges, all_paths, chromosome, init_pop, substrate, substrate_copy
):
    global x
    if x == True:
        return None
    # if i >= len(virtual_edges):
    #     return None
    if len(chromosome) == len(virtual_edges):
        flag = False
        substrate_copy = copy.deepcopy(substrate)
        for i in range(len(virtual_edges)):
            # print(f"chrom {chromosome}")
            path = chromosome[i]
            weight = virtual_edges[i]
            for j in range(1, len(path)):
                substrate_copy.edge_weights[(path[j - 1], path[j])] -= weight
                substrate_copy.edge_weights[(path[j], path[j - 1])] -= weight
                if substrate_copy.edge_weights[(path[j], path[j - 1])] < 0:
                    flag = True
                    break
            if flag == True:
                break
        if flag == False:
            init_pop.append(copy.deepcopy(chromosome))
            # print(f"appended : {len(init_pop)}  L : {chromosome}")
        if len(init_pop) == 8:
            x = True
            return None
    else:
        for gene in all_paths[i]:
            chromosome.append(gene)
            selectPaths(
                i + 1,
                virtual_edges,
                all_paths,
                chromosome,
                init_pop,
                substrate,
                substrate_copy,
            )
            chromosome.pop()

    # return None


def select_random_path(req_map, vne_list, req_no, all_paths, substrate):
    population = []
    population_set = set()
    curr_pop = 0
    counter = 0
    while curr_pop < 8 and counter < 1000:
        curr_map = temp_map(vne_list, req_no, req_map.node_map)
        for i in range(len(vne_list[req_no].edges) // 2):
            curr_map.edge_map.append(random.choice(all_paths[i]))
        if (
            check_compatibility(curr_map, copy.deepcopy(substrate), vne_list[req_no])
            and get_hashable_map(curr_map) not in population_set
        ):
            curr_pop += 1
            population.append(curr_map)
            population_set.add(get_hashable_map(curr_map))
        counter += 1
    return population

def findAvgPathLength(vnr):
    cnt=0
    for node1 in range(vnr.nodes):
        for node2 in range(vnr.nodes):
            if(node1 != node2):
                path = vnr.findShortestPath(str(node1), str(node2), 0)
                cnt += len(path)-1
    total_nodes = vnr.nodes
    cnt /= (total_nodes)*(total_nodes-1)
    return cnt


def edge_map(substrate, virtual, req_no, req_map, vne_list):
    substrate_copy = copy.deepcopy(substrate)
    all_paths = []
    virtual_edges = []
    for edge in virtual.edges:
        if int(edge[0]) > int(edge[1]):
            weight = virtual.edge_weights[edge]
            virtual_edges.append(weight)
            left_node = req_map.node_map[int(edge[0])]
            right_node = req_map.node_map[int(edge[1])]
            paths = substrate_copy.printAllPaths(
                str(left_node), str(right_node), weight
            )  # find all paths from src to dst
            # print(paths)
            if paths == []:
                return None
            all_paths.append(paths)
    initial_population = select_random_path(
        req_map, vne_list, req_no, all_paths, substrate_copy
    )

    return initial_population


def tournament_selection(elite_population, vne_list, req_no):
    random.shuffle(elite_population)
    # sz = len(elite_population) // 2
    # group1 = elite_population[:sz]
    # group2 = elite_population[sz:]
    # parent1 = temp_map(vne_list, req_no)
    # # confirm for fitness value
    # for j in range(len(group1)):
    #     if parent1.fitness < group1[j].fitness:
    #         parent1 = group1[j]
    # parent2 = temp_map(vne_list, req_no)
    # for j in range(len(group2)):
    #     if parent2.fitness < group2[j].fitness:
    #         parent2 = group2[j]
    parent1, parent2 = (elite_population[0], elite_population[1]) # for random selection of parents
    return parent1, parent2


def elastic_crossover(
    parent1, parent2, population_set, substrate, virtual, itr, elite_population
):  # itr is inside loop number
    if len(parent1.edge_map) <= 1:
        return None, None
    maxx = len(parent1.edge_map)
    maxx = int(0.75*(maxx))
    if maxx <= 1:
        return None, None
    parent2_copy = copy.deepcopy(parent2)
    parent1_copy = copy.deepcopy(parent1)
    parent1_pos = random.sample(
        range(len(parent1.edge_map)), random.randint(1, maxx - 1)
    )
    for i in parent1_pos:
        parent1.edge_map[i] = parent2_copy.edge_map[i]
        parent1.path_cost[i] = parent2_copy.path_cost[i]
    parent2_pos = random.sample(
        range(len(parent1.edge_map)), random.randint(1, maxx - 1)
    )
    for i in parent2_pos:
        parent2.edge_map[i] = parent1_copy.edge_map[i]
        parent2.path_cost[i] = parent1_copy.path_cost[i]
    if not check_compatibility(parent1, copy.deepcopy(substrate), virtual):
        # parent1 = None
        logging.warning(f"\t\t{itr}-could not add child1 due to incompatibility")
    elif get_hashable_map(parent1) in population_set:
        logging.warning(f"\t\t{itr}-Could not get distict child1")
        # parent1 = None
    else:
        parent1.fitness = get_fitness(parent1, virtual)
        parent1.edge_cost = sum(parent1.path_cost)
        parent1.total_cost = parent1.node_cost + parent1.edge_cost
        elite_population.append(parent1)
        population_set.add(get_hashable_map(parent1))
        logging.info(f"\t\t\t{i}-Added Crossovered Child1 {parent1.edge_map}\tfitness: {parent1.fitness:.4f}\ttot_cost: {parent1.total_cost}")

    if not check_compatibility(parent2, copy.deepcopy(substrate), virtual):
        # parent2 = None
        logging.warning(f"\t\t{itr}-could not add child2 due to incompatibility")
    elif get_hashable_map(parent2) in population_set:
        logging.warning(f"\t\t{itr}-could not get distict child2")
        # parent2 = None
    else:
        parent1.fitness = get_fitness(parent1, virtual)
        parent1.edge_cost = sum(parent1.path_cost)
        parent1.total_cost = parent1.node_cost + parent1.edge_cost
        elite_population.append(parent1)
        population_set.add(get_hashable_map(parent1))
        logging.info(f"\t\t\t{i}-Added Crossovered Child1 {parent2.edge_map}\tfitness: {parent2.fitness:.4f}\ttot_cost: {parent2.total_cost}")
    return parent1, parent2


def mutate(
    child, substrate, population_set, virtual, itr, elite_population
):  # itr is inside loop number
    random_no = random.randint(0, len(child.edge_map) - 1)
    sel_path = child.edge_map[random_no]
    edge = (str(sel_path[0]), str(sel_path[-1]))
    child.edge_map[random_no] = substrate.findPathFromSrcToDst(
        edge[0], edge[1], child.edge_weight[random_no]
    )
    child.path_cost[random_no] = (len(child.edge_map[random_no])-1)*child.edge_weight[random_no]
    if not check_compatibility(child, copy.deepcopy(substrate), virtual):
        child = None
        logging.warning(f"\t\t{itr}-could not add mutated_child due to incompatibility")
    elif get_hashable_map(child) in population_set:
        logging.warning(f"\t\t{itr}-Could not get distict mutated_child")
        child = None
    else:
        child.edge_cost = sum(child.path_cost)
        child.total_cost = (
            child.node_cost + child.edge_cost
        )
        child.fitness = get_fitness(
            child, virtual
        )
        elite_population.append(child)
        population_set.add(get_hashable_map(child))
        logging.info(f"\t\t\t{itr}-Added Muted Child {child.edge_map}\tfitness: {child.fitness:.4f}\ttot_cost: {child.total_cost}")
    return child


def get_hashable_map(chromosome):
    temp_list = []
    for path in chromosome.edge_map:
        temp_list.append(tuple(path))
    return tuple(temp_list)


def check_compatibility(chromosome, substrate_copy, virtual):
    for i, path in enumerate(chromosome.edge_map):
        for j in range(1, len(path)):
            edge = (str(path[j - 1]), str(path[j]))
            if (
                substrate_copy.edge_weights[edge]
                < virtual.edge_weights[virtual.edges[i]]
            ):
                return False
            else:
                substrate_copy.edge_weights[edge] -= virtual.edge_weights[virtual.edges[i]]
                edge = (str(path[j]), str(path[j-1]))
                substrate_copy.edge_weights[edge] -= virtual.edge_weights[virtual.edges[i]]
    return True


def import_elite(population):
    population = sorted(population, key=lambda x: x.fitness, reverse=True)
    if len(population) > 8:
        population = population[:8]
    population_set = set()
    for i in population:
        population_set.add(get_hashable_map(i))
    return population, population_set


def get_best_map(population):
    return sorted(population, key=lambda x: x.fitness, reverse=True)[0]


def substract_from_substrate(substrate, virtual, selected_map):
    for i, node in enumerate(selected_map.node_map):
        substrate.node_weights[node] -= virtual.node_weights[i]
    for i, path in enumerate(selected_map.edge_map):
        for j in range(1, len(path)):
            substrate.edge_weights[
                (str(path[j - 1]), str(path[j]))
            ] -= selected_map.edge_weight[i]
            substrate.edge_weights[
                (str(path[j]), str(path[j-1 ]))
            ] -= selected_map.edge_weight[i]


def get_fitness(chromosome, virtual):
    hop_count = 0
    delay_sum = 0
    wp = 1
    wh = 1
    wc = 1
    for i in range(len(virtual.edges) // 2):
        hop_count += len(chromosome.edge_map[i])
        delay_sum += hop_count - 1
    return (1 / chromosome.total_cost)* wc + (1 / hop_count)*wh + (1 / delay_sum)*wp
