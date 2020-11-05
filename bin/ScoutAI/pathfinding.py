# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #7: The Maze Decorator

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import os
import sys
import time
import json
import math

from priority_dict import priorityDictionary as PQ

def load_grid(world_state):
    """
    Used the agent observation API to get a 21 X 21 grid box around the agent (the agent is in the middle).

    Args
        world_state:    <object>    current agent world state

    Returns
        grid:   <list>  the world grid blocks represented as a list of blocks (see Tutorial.pdf)
    """
    while world_state.is_mission_running:
        #sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        if len(world_state.errors) > 0:
            raise AssertionError('Could not load grid.')

        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            observations = json.loads(msg)
            grid = observations.get(u'floorAll', 0)
            break
    return grid

def find_start_end(grid):
    """
    Finds the source and destination block indexes from the list.

    Args
        grid:   <list>  the world grid blocks represented as a list of blocks (see Tutorial.pdf)

    Returns
        start: <int>   source block index in the list
        end:   <int>   destination block index in the list
    """
    
    start = end = None

    for i, block in enumerate(grid):
        if (start and end):
            break
        if block == 'emerald_block':
            start = i
        if block == 'redstone_block':
            end = i
        
    return (start, end)

def extract_action_list_from_path(path_list):
    """
    Converts a block idx path to action list.

    Args
        path_list:  <list>  list of block idx from source block to dest block.

    Returns
        action_list: <list> list of string discrete action commands (e.g. ['movesouth 1', 'movewest 1', ...]
    """
    action_trans = {-21: 'movenorth 1', 21: 'movesouth 1', -1: 'movewest 1', 1: 'moveeast 1'}
    alist = []
    for i in range(len(path_list) - 1):
        curr_block, next_block = path_list[i:(i + 2)]
        alist.append(action_trans[next_block - curr_block])

    return alist

def dijkstra_shortest_path(grid_obs, source, dest, danger_blocks = []):
    """
    Finds the shortest path from source to destination on the map. It used the grid observation as the graph.
    See example on the Tutorial.pdf file for knowing which index should be north, south, west and east.

    Args
        grid_obs:   <list>  list of block types string representing the blocks on the map.
        source:     <int>   source block index.
        dest:       <int>   destination block index.

    Returns
        path_list:  <list>  block indexes representing a path from source (first element) to destination (last)
    """

    action_trans = {'north': -21, 'south': 21, 'west': -1, 'east': 1}

    path_set = set() # indexes
    priority_dict = PQ() # key = index, value = distance value
    parent = [-1] * len(grid_obs)
    for i in range(0, len(grid_obs)):
        if (grid_obs[i] in danger_blocks):
            continue
        priority_dict[i] = math.inf
    priority_dict[source] = 0

    while (len(priority_dict) != 0):
        # picking vertex with minimum distance (smallest() from priority queue) and is not in the path set
        # priority dict should not contain vertices added to path_list
        smallest_vertex = priority_dict.smallest()
        smallest_vertex_distance = priority_dict[smallest_vertex]


        # adding u to the path set
        path_set.add(smallest_vertex)
        # removing from priority dict
        priority_dict.pop(smallest_vertex)

        for adj_index in [smallest_vertex + modifier for modifier in action_trans.values()]:
            if adj_index in priority_dict:
                # sum of distance value u (in priority queue) and edge u-v (always 1)
                new_distance_value = smallest_vertex_distance + 1
                v_distance_value = priority_dict[adj_index]
                if (new_distance_value < v_distance_value):
                    # update if new distance value is less than value saved in data structure
                    priority_dict[adj_index] = new_distance_value
                    # update parent
                    parent[adj_index] = smallest_vertex
            
            
    # generating shortest path utilizing parents (in reverse order)
    path_list = [dest]
    while (True):
        current_parent = parent[path_list[-1]]
        if (current_parent == -1):
            break
        path_list.append(current_parent)

    return list(reversed(path_list))
