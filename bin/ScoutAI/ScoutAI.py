import pathfinding as pf
from collections import deque

DEBUG = True

class ScoutAI:

    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.action_stack = deque()

    def move_south(self):
        return 'movesouth 1'

    def go_to_redstone_block(self, world_state):
        grid = pf.load_grid(self.agent_host, world_state)
        start, end = pf.find_start_end(grid)
        path = pf.dijkstra_shortest_path(grid, start, end, danger_blocks=['air', 'lava_block'])
        
        self.action_stack.clear()
        self.action_stack.extend(pf.extract_action_list_from_path(path))

        if DEBUG:
            print("Output (start,end): ", (start,end))
            print("Output (path length): ", len(path))
            print("Output (actions): ", self.action_stack)
        

    def get_next_action(self):
        action = self.action_stack.popleft()
        return action
