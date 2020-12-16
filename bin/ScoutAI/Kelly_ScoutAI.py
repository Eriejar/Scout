# Scout AI

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import os
import sys
import time
import malmoutils
import json
import random
from tqdm import tqdm
from collections import deque
import matplotlib.pyplot as plt 
import numpy as np
from numpy.random import randint

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from ScoutAI import ScoutAI 
from CommandQueue import CommandQueue
from threading import Thread

sys.path.append('../')
from HandSignDetection import camera

SIZE = 10
OBS_SIZE = 5
MAX_EPISODE_STEPS = 100

MalmoPython.setLogging("", MalmoPython.LoggingSeverityLevel.LOG_OFF)

def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    print("Starting Mission {}.".format(role))
    max_retries = 5    
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expId)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2)

def safeWaitForStart(agent_hosts):
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow a two minute timeout.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            exit(1)
        time.sleep(0.1)
        print(".", end=' ')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start.")
        exit(1)
    print()
    print("Mission has started.")

def buildEnvironment():

    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                <About>
                    <Summary>Trainer</Summary>
                </About>

                <ServerSection>
                    <ServerInitialConditions>
                        <Time>
                            <StartTime>0</StartTime>
                            <AllowPassageOfTime>true</AllowPassageOfTime>
                        </Time>
                        <Weather>clear</Weather>
                    </ServerInitialConditions>
                    <ServerHandlers>
                        <FlatWorldGenerator generatorString="3;7,2;1;"/>
                        <DrawingDecorator>''' + \
                            "<DrawCuboid x1='{}' x2='{}' y1='2' y2='2' z1='{}' z2='{}' type='air'/>".format(-SIZE, SIZE, -SIZE, SIZE) + \
                            "<DrawCuboid x1='{}' x2='{}' y1='1' y2='1' z1='{}' z2='{}' type='stone'/>".format(-SIZE, SIZE, -SIZE, SIZE) + \
                            '''<DrawBlock x='0'  y='2' z='0' type='air' />
                            <DrawBlock x='5' y='1' z='5' type='redstone_block' />
                            <DrawBlock x='0' y='1' z='0' type='emerald_block' />
                            <DrawEntity x='1' y='2' z='10' type="Cow" />
                            <DrawEntity x='10' y='2' z='20' type="Wolf" />
                            <DrawBlock x='8' y='2' z='10' type='diamond_block' />
                        </DrawingDecorator>
                        <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                </ServerSection>

                <AgentSection mode="Survival">
                    <Name>Trainer</Name>
                    <AgentStart>
                        <Placement x="5.5" y="2" z="5.5" pitch="0" yaw="90"/>
                        <Inventory>
                            <InventoryItem slot="0" type="diamond_pickaxe"/>
                        </Inventory>
                    </AgentStart>
                    <AgentHandlers>
                        <DiscreteMovementCommands/>
                        <ObservationFromFullStats/>
                        <RewardForCollectingItem>
                            <Item type="diamond" reward="1.0"/>
                        </RewardForCollectingItem>
                        <RewardForTouchingBlockType>
                            <Block reward="-1.0" type="lava"/>
                        </RewardForTouchingBlockType>
                        <ObservationFromGrid>
                            <Grid name="floorAll">
                                <min x="-10" y="-1" z="-10"/>
                                <max x="10" y="-1" z="10"/>
                            </Grid>
                        </ObservationFromGrid>
                        <AgentQuitFromReachingCommandQuota total="'''+str(MAX_EPISODE_STEPS)+'''" />
                    </AgentHandlers>
                </AgentSection> 

                
                <AgentSection mode="Survival">
                    <Name>Scout</Name>
                    <AgentStart>
                        <Placement x="0.5" y="2" z="0.5" pitch="45" yaw="0"/>
                        <Inventory>
                            <InventoryItem slot="0" type="diamond_pickaxe"/>
                        </Inventory>
                    </AgentStart>
                    <AgentHandlers>
                        <DiscreteMovementCommands/>
                        <ObservationFromFullStats/>
                        <RewardForCollectingItem>
                            <Item type="diamond" reward="1.0"/>
                        </RewardForCollectingItem>
                        <RewardForTouchingBlockType>
                            <Block reward="-1.0" type="lava"/>
                        </RewardForTouchingBlockType>
                        <ObservationFromGrid>
                            <Grid name="floorAll">
                                <min x="-10" y="-1" z="-10"/>
                                <max x="10" y="-1" z="10"/>
                            </Grid>
                        </ObservationFromGrid>
                        <AgentQuitFromReachingCommandQuota total="'''+str(MAX_EPISODE_STEPS)+'''" />
                    </AgentHandlers>
                </AgentSection> 

            </Mission>''' 

def identify_command(command):
    if command == 0:
        return None

    if command == 1:
        return 1

    if command == 2:
        return 2
   
    if command == 3:
        return 3

    if command == 4:
        return 4
    
    if command == 5:
        return 5



if __name__ == '__main__':
    # Create default Malmo objects:
    agent_host = MalmoPython.AgentHost()
    #scout_ai = ScoutAI(agent_host)
    scout_ai = MalmoPython.AgentHost()
    malmoutils.parse_command_line(agent_host)
    commandQueue = CommandQueue()
    prev_command = 0
    counter = 0

    my_mission = MalmoPython.MissionSpec(buildEnvironment(),True)
    my_mission.allowAllChatCommands()
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo( "127.0.0.1", 10000) )
    client_pool.add(MalmoPython.ClientInfo( "127.0.0.1", 10001) )
    agent_host_record = MalmoPython.MissionRecordSpec()
    scout_record = MalmoPython.MissionRecordSpec()

    safeStartMission(agent_host, my_mission, client_pool, agent_host_record,0,'')
    safeStartMission(scout_ai, my_mission, client_pool, scout_record,1,'')

    safeWaitForStart([agent_host,scout_ai])

    inference_thread = Thread(target = camera.real_annotate)
    inference_thread.start()
    while agent_host.peekWorldState().is_mission_running or scout_ai.peekWorldState().is_mission_running:    
        command = camera.gesture_this_frame
        command = identify_command(command)
        if not command is None:
            if prev_command == command:
                counter += 1
            else:
                counter = 0
            prev_command = command
            if counter >= 2:
                commandQueue.add_command(command)
        print(commandQueue.commands)
        # Check if user has signaled for Scout to execute actions
        if len(commandQueue.commands) > 0 and commandQueue.commands[-1] == 5:
            # Execute each command in the Command Queue
            for i in range(len(commandQueue.commands)):
                agent_host.sendCommand("chat" + str(commandQueue.execute_command() ) + str(1))
            prev_command = 0
        
    camera.run_thread = False
    inference_thread.join()
    print("Mission end")
    exit(1)
    '''
    try:
        agent_host.parse( sys.argv )
    except RuntimeError as e:
        print('ERROR:', e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)
    role = 0
    print(sys.argv)
    if len(sys.argv) >= 2:
        role = sys.argv[3]
        print("Will run as role", role)
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo( "127.0.0.1", 10000) )
    client_pool.add(MalmoPython.ClientInfo( "127.0.0.1", 10001) )
    
    my_mission = MalmoPython.MissionSpec(buildEnvironment(),True)
    my_mission_record = MalmoPython.MissionRecordSpec()
   
    
    # Attempt to start a mission:
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, client_pool, my_mission_record, int(role), "MMExp#1" )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:",e)
                exit(1)
            else:
                time.sleep(2)

    # Loop until mission starts:
    print("Waiting for the mission to start ", end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)

    print()
    print("Mission running ", end=' ')


    scout_ai.go_to_redstone_block(world_state)
    action_index = 0
    numActions = len(scout_ai.action_stack)
    # Loop until mission ends:
    while world_state.is_mission_running:
        #print(".", end="")
        time.sleep(0.1)
        if len(scout_ai.action_stack) == 0:
            time.sleep(2)
        else:
            agent_host.sendCommand(scout_ai.get_next_action())
        action_index += 1

        if numActions == action_index:
            time.sleep(2)

        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)

    print()
    print("Mission ended")
    # Mission has ended.
  
    '''
    #train(agent_host)
    
