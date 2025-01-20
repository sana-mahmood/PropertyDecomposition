import network_lib as Network
import copy
import sys

class Transition:
    def __init__(self, origin, destination, condition):
        self.origin = origin
        self.destination = destination
        self.condition = condition

class Node:
    def __init__(self, id, accepting):
        self.ID = id
        self.is_accepting = accepting
        self.transitions = []
        self.dependant_params = []
        self.undefined_transition = False
        self.is_trap = False

    def add_transition(self, dep_params, trans):
        for param in dep_params:
            if param not in self.dependant_params:
                self.dependant_params.append(param)
        self.transitions.append(trans)


    def undefined_transitions(self):
        return self.undefined_transition

    def execute_transitions(self):
        next_nodes = []
        self.undefined_transition = True
        for transition in self.transitions:
            if transition.condition():
                self.undefined_transition = self.undefined_transition and False
                next_nodes.append(transition.destination)
            else:
                self.undefined_transition = self.undefined_transition and True

        if len(next_nodes) == 0:
            return None
        else:
            return next_nodes

    def is_dependant_param(self, param):
        if param in self.dependant_params:
            return True
        else:
            return False


class BuchiAutomata:
    def __init__(self, node, deter=True):
        self.start_node = node.ID
        self.current_nodes = [node.ID]
        self.callback_params = []
        self.all_nodes = {node.ID: node}
        self.deterministic = deter

    def modification_callback(self, param_name):
        all_none = True
        new_current_nodes = []
        dependant_param = False
        for i in range(len(self.current_nodes)):
            node = self.all_nodes[self.current_nodes[i]]
            if not node.is_dependant_param(param_name): continue
            dependant_param = True
            next_node_id_list = node.execute_transitions()
            if next_node_id_list is not None:
                new_current_nodes.extend(next_node_id_list)
                all_none = False

        if dependant_param:
            if all_none:
                exception_str = "Undefined Transition!"
                for i in range(len(self.current_nodes)):
                    exception_str+" -- "
                    node = self.all_nodes[self.current_nodes[i]]
                    exception_str+=" Automation State: "+str(node.ID) + " [ "+param_name+": "+str(Network.Values[param_name]) + ", hop_count: " + str(Network.Values[Network.HOP_COUNT]) +" ]"
                raise Exception(exception_str)

            self.current_nodes = new_current_nodes

    def add_node(self, node):
        self.all_nodes[node.ID] = node

    def add_transition(self, param_names, cond_stmt, org, dst):
        self.all_nodes[org].add_transition(param_names, Transition(org, dst, cond_stmt))
        for param in param_names:
            if param not in self.callback_params:
                self.callback_params.append(param)
                Network.add_callback(param, self.modification_callback)

    def is_deterministic(self):
        return True

    def remove_callbacks(self):
        for param in self.callback_params:
            Network.remove_callback(param, self.modification_callback)

    def reset(self):
        self.current_nodes = [self.start_node]


def decompose_safety(automata):
    safety_automata = copy.deepcopy(automata)

    for id, node in safety_automata.all_nodes.items():
        node.is_accepting = True

    for param in safety_automata.callback_params:
        Network.add_callback(param, safety_automata.modification_callback)

    return safety_automata


def decompose_liveness(automata):
    live_automata = copy.deepcopy(automata)

    trap_id = len(live_automata.all_nodes.keys())+1
    trap = Node(trap_id, True)
    trap.is_trap = True
    live_automata.add_node(trap)

    def always_true():
        return True
    live_automata.add_transition(live_automata.callback_params, always_true, trap_id, trap_id)

    for id, node in live_automata.all_nodes.items():
        if id == trap_id:
            continue

        # direct undefined transition to trap node
        live_automata.add_transition([], node.undefined_transitions, node.ID, trap_id)

        if not automata.is_deterministic():
            node.is_accepting = False

    for param in live_automata.callback_params:
        Network.add_callback(param, live_automata.modification_callback)

    if automata.is_deterministic():
        return [1, live_automata]
    else:
        return [2, live_automata]


