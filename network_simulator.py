import xml.etree.ElementTree as ET
import network_lib as N
from enum import Enum

EXPLORE_ALL_PATHS = False

class Action(Enum):
    DROP = "DROP"
    OUT_PORT = "OUT_PORT"
    DELETE_RULE = "DELETE_RULE"
    ADD_RULE = "ADD_RULE"

class Counters:
    def __init__(self):
        self.pin = 0
        self.pout = 0
        self.pdrop = 0


class Port:
    def __init__(self, ID):
        self.ID = ID
        self.counters = Counters()


class Rule:
    def __init__(self, id, src, dst, priority, in_port, out_port, metric, protocol, action: Action, active=True, rules=[]):
        self.ID = id
        self.src = src
        self.dst = dst
        self.priority = priority
        self.in_port = in_port
        self.out_port = out_port
        self.metric = metric
        self.protocol = protocol
        self.action = action
        self.active = active
        self.rules = rules

class Packet:
    def __init__(self, src, dst, metric, protocol, ecn=0, dscp=0):
        self.src = src
        self.dst = dst
        self.metric = metric
        self.in_port = None  # This will be set when the packet arrives at a node
        self.protocol = protocol
        self.ecn = ecn
        self.dscp = dscp


class Node:
    def __init__(self, ID, type):
        self.ID = ID
        self.type = type
        self.ports = {}
        self.routing_table = []
        self.connections = {}  # port id to (connected node id, connected port id) mapping

class Network:
    def __init__(self, filename):
        self.node_dict = {}
        self.load_network(filename)

    # Function to parse XML and load data into the node dictionary
    def parse_xml(self, xml_data):
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()

        # First, parse all nodes and create empty Node objects
        for node_elem in root.findall('node'):
            node_id = node_elem.get('id')
            node_type = node_elem.get('type')
            self.node_dict[node_id] = Node(node_id, node_type)

        # Then, fill in ports, routing tables, and connections
        for node_elem in root.findall('node'):
            node_id = node_elem.get('id')
            node = self.node_dict[node_id]

            # Load Ports and Connections
            for port_elem in node_elem.find('ports').findall('port'):
                port_id = int(port_elem.get('id'))
                node.ports[port_id] = Port(port_id)

                # Load Connections
                connection_elem = port_elem.find('connection')
                if connection_elem is not None:
                    connected_node_id = connection_elem.get('node')
                    connected_port_id = int(connection_elem.get('port'))

                    # Add connection for the current node
                    node.connections[port_id] = (connected_node_id, connected_port_id)

            # Load Routing Table
            for rt_elem in node_elem.find('routingTable').findall('entry'):
                id = rt_elem.get('id')
                src = rt_elem.get('src')
                dst = rt_elem.get('dst')
                priority = rt_elem.get('priority')
                in_port = rt_elem.get('inPort')
                out_port = rt_elem.get('outPort')
                metric = rt_elem.get('metric')
                protocol = rt_elem.get('protocol')
                action = rt_elem.get('action')
                active = rt_elem.get('active')
                rules = rt_elem.get('rules')

                routing_entry = Rule(
                    id=id if id is not None else None,
                    src=src if src is not None else None,
                    dst=dst if dst is not None else None,
                    priority=int(priority) if priority is not None else 100,
                    in_port=int(in_port) if in_port is not None else None,
                    out_port=int(out_port) if out_port is not None else None,
                    metric=int(metric) if metric is not None else None,
                    protocol=int(protocol) if protocol is not None else None,
                    action=Action(action) if action is not None else None,
                    active=bool(int(active)) if active is not None else True,
                    rules=rules.split() if rules is not None else []
                )

                node.routing_table.append(routing_entry)

    def load_network(self, filename):
        xml_data = open(filename).read()
        self.parse_xml(xml_data)

    def receive_packet(self, node, packet, in_port):
        # TODO This is wrong!! why am i sending packet on multiple paths!! it should just randomly pick one
        """
        Process an incoming packet and forward it if a match is found in the routing table.
        """
        if in_port != -1:
            N.set_value(N.HOP_COUNT, N.Values[N.HOP_COUNT] + 1)
            N.set_value(N.NODE_TYPE, node.type)
            N.set_value(N.CURRENT_NODE, node.ID)

        if (node.type == "server" and in_port != -1) or node.type == "Internet Gateway":
            if packet.dst == node.ID:
                N.set_value(N.HOP_COUNT, N.Values[N.HOP_COUNT] - 1)
                # if (N.Values[N.HOP_COUNT] < 1): print("in DST RETURN")
                return True
            else:
                print("Wrong destination!!")
                N.set_value(N.HOP_COUNT, N.Values[N.HOP_COUNT] - 1)
                if (N.Values[N.HOP_COUNT] < 1): print("in WRONG DST RETURN")
                return False

        packet.in_port = in_port

        best_entry = None
        matched_entries = []

        # Look for a matching routing table entry with highest priority
        for entry in node.routing_table:
            if (entry.src is None or entry.src == packet.src or entry.src == "ANY") and \
                    (entry.dst is None or entry.dst == packet.dst or entry.dst == "ANY") and \
                    (entry.in_port is None or entry.in_port == packet.in_port) and \
                    (entry.protocol is None or entry.protocol == packet.protocol) and \
                    (entry.metric is None or entry.metric == packet.metric and entry.active):  # Match on all fields

                # Check for the best matching entry based on priority
                if best_entry is None or entry.priority > best_entry.priority:
                    best_entry = entry
                    matched_entries.append(
                        entry)  # this list can have entries with lower priority so we need to filter them later
                elif entry.priority == best_entry.priority:
                    matched_entries.append(entry)

        res = None
        new_path = False
        if best_entry:
            for entry in matched_entries:
                if new_path:
                    N.set_value(N.PATH_ID, N.Values[N.PATH_ID] + 1)
                    N.set_value(N.NODE_TYPE, node.type)
                    N.set_value(N.CURRENT_NODE, node.ID)
                if entry.priority < best_entry.priority: continue

                # Forward the packet based on the best matching entry
                if entry.action == Action.DROP:
                    N.set_value(N.DROP_NODE, node.ID)
                    N.set_value(N.DROPPED, True)
                    N.Values[N.DROPPED] = False
                    N.set_value(N.HOP_COUNT, N.Values[N.HOP_COUNT] - 1)
                    if (N.Values[N.HOP_COUNT] < 1): print("in DROP")
                    return None  # Packet is dropped

                elif entry.action == Action.OUT_PORT:
                    out_port = entry.out_port
                    if out_port in node.connections:
                        next_node_id, next_node_port = node.connections[out_port]
                        next_node = self.node_dict[next_node_id]
                        res = self.receive_packet(next_node, packet, next_node_port)
                    else:
                        print(f"Node {node.ID}: No connection found on port {out_port}, cannot forward packet")
                    if EXPLORE_ALL_PATHS:
                        new_path = True
                    else:
                        break
                elif entry.action == Action.DELETE_RULE:
                    x = 1
                elif entry.action == Action.ADD_RULE:
                    y = 1

        else:
            N.set_value(N.DROP_NODE, node.ID)
            N.set_value(N.DROPPED, True)
            N.Values[N.DROPPED] = False  # resetting it since the operation has been accounted for

        N.set_value(N.HOP_COUNT, N.Values[N.HOP_COUNT] - 1)
        # if (N.Values[N.HOP_COUNT] < 1): print("in MAIN RETURN", N.Values[N.CURRENT_NODE], node.ID)
        return res

    def server_send(self, src, dst):
        packet = Packet(src=src, dst=dst, metric=None, protocol=None)
        # Start packet transmission at node 1, arriving on port 101
        N.set_value(N.SOURCE, src)
        # print("sending from", src, "to", dst)
        self.receive_packet(self.node_dict[src], packet, in_port=-1)
