from network_lib import *
import verification_interface
from bucchi_automata import *

hops = 0

dst = None
k=4

CoreSwitchIDs= []
AggregationSwitchIDs= []
EdgeSwitchIDs= []
ServerIDs= []

if k == 4:
    CoreSwitchIDs= [0, 1, 2, 3]
    AggregationSwitchIDs= [4, 5, 6, 7, 8, 9, 10, 11]
    EdgeSwitchIDs= [12, 13, 14, 15, 16, 17, 18, 19]
    ServerIDs= [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]

elif k == 8:
    CoreSwitchIDs= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    AggregationSwitchIDs= [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
    EdgeSwitchIDs= [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79]
    ServerIDs= [80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207]


def not_originate_from_src():
    return not (originate_from_src())

def originate_from_src():
    if int(Values[SOURCE]) in ServerIDs:
        return True
    else:
        return False

def path_continues_without_end_node():
    global hops
    if Values[HOP_COUNT] <= hops:
        return False
    else:
        hops += 1

    if Values[NODE_TYPE] == "server":
        return False
    else:
        return True

def path_continues_without_waypoint_or_end_node():
    global hops
    if Values[HOP_COUNT] <= hops:
        return False
    else:
        hops += 1

    if int(Values[CURRENT_NODE]) in CoreSwitchIDs or Values[NODE_TYPE] == "server":
        return False
    else:
        return True

def pass_waypoint():
    if int(Values[CURRENT_NODE]) in CoreSwitchIDs:
        return True
    else:
        return False

def reached_destination():
    if Values[CURRENT_NODE] == dst:
        return True
    else:
        return False

def new_path_pre_waypoint():
    global hops
    hops = Values[HOP_COUNT]-1

    if Values[HOP_COUNT] < 3:
        return True
    else:
        return False

def new_path_post_waypoint():
    global hops
    hops = Values[HOP_COUNT]-1

    if Values[HOP_COUNT] >= 3:
        return True
    else:
        return False

def true_func():
    return True


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
automata.add_transition([Network.PATH_ID], new_path_pre_waypoint, 4, 2)
automata.add_transition([Network.PATH_ID], new_path_post_waypoint, 4, 3)
# automata.add_transition([Network.PATH_ID], new_path_pre_waypoint(), 4, 2)
def reset_params():
    global hops
    hops = 0

start_time = time.time()

servers_per_pod = (k // 2) ** 2
num_pods = k  # The number of pods is equal to k in a k-ary fat tree.

violations = 0
# Loop over each pod
# for pod_id in range(num_pods):
#     # Get the range of servers in this pod
#     pod_start = pod_id * servers_per_pod
#     pod_end = pod_start + servers_per_pod
#
#     # Loop over each server in this pod
#     for src_server in range(pod_start, pod_end):
#         # Send packets from this server to all servers outside the pod
#         for dst_server in range(len(ServerIDs)):
#             if dst_server < pod_start or dst_server >= pod_end:
#                 src_server_id = str(ServerIDs[src_server])
#                 dst_server_id = str(ServerIDs[dst_server])
#                 dst = str(ServerIDs[dst_server])
#                 reset_params()
#                 op = verification_interface.explore_all_paths(["fat_tree_"+str(k)+"_topology.xml", "fat_tree_"+str(k)+"_topology.xml", "fat_tree_"+str(k)+"_topology.xml", "fat_tree_"+str(k)+"_topology.xml", "fat_tree_"+str(k)+"_topology.xml", "fat_tree_"+str(k)+"_topology.xml"],
#                                                          src_server_id, dst_server_id, "L", automata, reset_params)

src_pod = 0
dst_pod = num_pods//2
while src_pod < num_pods//2 and dst_pod < num_pods:
    # Get the range of servers in this pod
    s_pod_start = src_pod * servers_per_pod
    s_pod_end = s_pod_start + servers_per_pod

    d_pod_start = dst_pod * servers_per_pod
    d_pod_end = d_pod_start + servers_per_pod

    while s_pod_start < s_pod_end and d_pod_start < d_pod_end:
        src = str(ServerIDs[s_pod_start])
        dst = str(ServerIDs[d_pod_start])
        reset_params()
        op = verification_interface.explore_all_paths(
            ["fat_tree_" + str(k) + "_topology.xml", "fat_tree_" + str(k) + "_topology.xml",
             "fat_tree_" + str(k) + "_topology.xml", "fat_tree_" + str(k) + "_topology.xml",
             "fat_tree_" + str(k) + "_topology.xml", "fat_tree_" + str(k) + "_topology.xml"],
            src, dst, "L", automata, reset_params)
        s_pod_start+=1
        d_pod_start+=1
    src_pod+=1
    dst_pod+=1


# Record the end time
end_time = time.time()

# Calculate and print the execution time
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")
if violations == 0:
    print("No violations")
else:
    print("violations found: ", violations)
#
# NOTE:
#
# So the reaosn they are failing is because of the "Explore all paths thing"
#     when destination aggregate looks at the other path, tha waypoint situation is never fulfilled.
#     So i need to update the "new path" function where it returns true only when its a new path outside of destination pod
#
# Another thing to fix:
#     I need to reset the safety automata everytime we look at new server pairs.
#     maybe not unhook callbacks but just go to state 0
#
# Another thing to fix:
#     in the generate fat tree code: update the code to be destination based (not src and dst based rules)
#     this will make things more realistic and fast