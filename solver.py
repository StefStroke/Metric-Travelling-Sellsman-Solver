import os
import sys

sys.path.append('..')
sys.path.append('../..')
import argparse
import utils

from graph import *
from student_utils import *
from prims import *

"""
======================================================================
  Complete the following function.
======================================================================
"""


def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """
    starting_index = list_of_locations.index(starting_car_location)
    graph = recover_graph(list_of_locations, list_of_homes, adjacency_matrix, starting_index)
    mst = prims(graph, starting_index)
    d = drop_off(mst, list_of_locations, list_of_homes)
    path1 = []
    pre_order(mst, starting_index, path1)
    path2 = parse_path(graph, path1)  # input graph or mst1 or mst 2 or doesn't matter?
    return path2, d


# adj matrix is a 2d list
def recover_graph(list_of_locations, list_of_homes, adjacency_matrix, starting_index):
    g = Graph()
    for i in range(len(list_of_locations)):
        g.addVertex(i)
        if list_of_locations[i] in list_of_homes:
            g.getVertex(i).makeHome()
    g.getVertex(starting_index).makeSrc()
    for i in range(len(list_of_locations)):
        for j in range(len(list_of_locations)):
            w = adjacency_matrix[i][j]
            if w != 'x':
                g.addEdge(i, j, w)
    return g


def drop_off(min_tree, list_of_locations, list_of_homes):
    """
    takes in a graph and outputs:
        1. a reduced graph
        2. a dictionary with key value pairs indicating drop off location
            and the TAs who're dropped off
            key: dropoff location
            value: a list of TA homes to go to
    """
    leaf_nodes = []
    for l in range(len(list_of_locations)):
        if min_tree.getVertex(l) and min_tree.getVertex(l).isLeaf():
            leaf_nodes.append(l)
    # or leaf_nodes = [i for i in range(len(list_of_homes)) if mst.getVertex(i).isLeaf]
    # assuming that all leaves must be home
    d = {}
    for l in leaf_nodes:
        drop_loc = min_tree.deleteLeaf(l)
        if drop_loc is None:
            continue
        if drop_loc not in d.keys():
            d[drop_loc] = set()
        d[drop_loc].add(l)
        if min_tree.getVertex(drop_loc).isHome():
            # print("current dict: ", d)
            d[drop_loc].add(drop_loc)
    for h in list_of_homes:
        h_id = list_of_locations.index(h)
        if h_id in min_tree.vet_list.keys():
            if h_id not in d.keys():
                d[h_id] = set()
                d[h_id].add(h_id)
    for key in d.keys():
        d[key] = list(d[key])

    return d


def pre_order(tree, src, path):  # src: vertex id
    v = tree.getVertex(src)
    path.append(src)
    for n in v.getNeighbor().keys():
        if n.getID() not in path:
            pre_order(tree, n.getID(), path)
    return


def parse_path(graph, path1):
    final_path = []
    starting_index = path1[0]
    final_path.append(starting_index)
    while len(path1) > 1:
        first = path1[0]
        second = path1[1]
        vfirst = graph.getVertex(first)
        vsecond = graph.getVertex(second)
        if vsecond in vfirst.getNeighbor().keys():
            final_path.append(second)
            path1.pop(0)
        else:
            path, weight = dijsktra(graph, first, [second])
            path.pop()
            while len(path) > 0:
                final_path.append(path.pop())
            path1.pop(0)
    lastpath, weight = dijsktra(graph, path1[0], [starting_index])
    lastpath.pop()
    while len(lastpath) > 0:
        final_path.append(lastpath.pop())
    return final_path


"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""


def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)


def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(
        input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true',
                        help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.',
                        help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
