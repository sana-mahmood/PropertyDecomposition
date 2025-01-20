from network_lib import *
import verification_interface
from bucchi_automata import *
import network_simulator as net_sim
import time

hops = 0

def not_originate_from_src():
    return not (originate_from_src())

def originate_from_src():
    if Values[SOURCE] == "2" or Values[SOURCE] == "3":
        return True
    else:
        return False

def path_continues_without_waypoint_or_end_node():
    global hops
    if Values[HOP_COUNT] <= hops:
        return False
    else:
        hops += 1

    if Values[NODE_TYPE] == "Access Point" or Values[NODE_TYPE] == "Internet Gateway":
        return False
    else:
        return True

def path_continues_without_end_node():
    global hops
    if Values[HOP_COUNT] <= hops:
        return False
    else:
        hops += 1

    if Values[NODE_TYPE] == "Internet Gateway":
        return False
    else:
        return True

def pass_waypoint():
    if Values[CURRENT_NODE] == "1":
        return True
    else:
        return False

def reached_destination():
    if Network.Values[Network.CURRENT_NODE] == "7":
        return True
    else:
        return False

def new_path():
    global hops
    hops = Values[HOP_COUNT]
    return True

def true_func():
    return True

def reset_params():
    global hops
    hops = 0

q0 = Node(0, False)
automata = BuchiAutomata(q0)
q1 = Node(1, True)
automata.add_node(q1)
q2 = Node(2, False)
automata.add_node(q2)
q3 = Node(3, False)
automata.add_node(q3)
q4 = Node(4, True)
automata.add_node(q4)


automata.add_transition([Network.SOURCE], not_originate_from_src, 0, 1)
automata.add_transition([], true_func, 1, 1)
automata.add_transition([Network.SOURCE], originate_from_src, 0, 2)
automata.add_transition([Network.CURRENT_NODE], path_continues_without_waypoint_or_end_node, 2, 2)
automata.add_transition([Network.CURRENT_NODE], pass_waypoint, 2, 3)
automata.add_transition([Network.CURRENT_NODE], path_continues_without_end_node, 3, 3)
automata.add_transition([Network.CURRENT_NODE], reached_destination, 3, 4)
automata.add_transition([Network.PATH_ID], new_path, 4, 2)

start_time = time.time()
op = True

op = op and verification_interface.explore_all_paths(["home_network_0.xml", "home_network_0.xml", "home_network_0.xml", "home_network.xml"],
                                                     "4", "7", "L", automata, reset_params)
reset_params()
op = op and verification_interface.explore_all_paths(["home_network_0.xml", "home_network_0.xml", "home_network_0.xml", "home_network.xml"],
                                                     "2", "7", "L", automata, reset_params)
reset_params()
op = op and verification_interface.explore_all_paths(["home_network_0.xml", "home_network_0.xml", "home_network_0.xml", "home_network.xml"],
                                                     "3", "7", "L", automata, reset_params)
reset_params()

# Record the end time
end_time = time.time()

# Calculate and print the execution time
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")
