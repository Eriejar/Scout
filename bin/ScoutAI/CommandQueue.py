from collections import deque 

class CommandQueue:
    def __init__(self):
        self.commands = deque()
    
    def add_command(self, command):
        # Add command to the command queue at the index signaled by the user
        self.commands.append(command)
        #commands.insert(index+1, command)
    
    def execute_command(self):
        # Return the next command in the command queue and pop it
        if len(self.commands) > 0:
            next_command = self.commands[0]
            self.commands.popleft()
        return next_command
    
    def reset(self):
        # Clear the command queue
        self.commands.clear()
