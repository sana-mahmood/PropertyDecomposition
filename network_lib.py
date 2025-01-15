import time
START_TIME = "start_time"
CURRENT_NODE = "current_node" # node id being traversed
PATH_ID = "path_id" # id of path/route being traversed
PROCESS_ID = "process_id"
HOP_COUNT = "hop_count"
SOURCE = "source"
DROPPED = "dropped"
DROP_NODE = "drop_node"
DROP_PORT = "drop_port"
TABLE_ENTRY = "table_entry" # the packet reached at a destination
NODE_TYPE = "node_type"

Values = {}
Callbacks = {}
Default = {}

Default[CURRENT_NODE] = None
Default[PATH_ID] = 1
Default[PROCESS_ID] = None
Default[HOP_COUNT] = 0
Default[SOURCE] = None
Default[DROPPED] = False
Default[DROP_NODE] = None
Default[DROP_PORT] = None
Default[NODE_TYPE] = None
Default[START_TIME] = time.time()

Values[CURRENT_NODE] = None
Values[PATH_ID] = 1
Values[PROCESS_ID] = None
Values[HOP_COUNT] = 0
Values[SOURCE] = None
Values[DROPPED] = False
Values[DROP_NODE] = None
Values[DROP_PORT] = None
Values[NODE_TYPE] = None
Values[START_TIME] = time.time()

for param in Values:
    Callbacks[param] = []


def add_variable(name, value=None):
    Values[name] = value
    Callbacks[name] = []

def set_value(name, new_value):
    if name in Values and Values[name] != new_value:
        Values[name] = new_value
        trigger_callbacks(name)

def add_callback(name, callback):
    if name in Values:
        Callbacks[name].append(callback)

def remove_callback(name, callback):
    if name in Callbacks:
        if callback in Callbacks[name]:
            Callbacks[name].remove(callback)


def trigger_callbacks(name):
    for callback in Callbacks[name]:
        callback(name)


def get_time_elapsed():
    return time.time() - Values[START_TIME]

def reset_vals():
    for param in Callbacks.keys():
        Values[param] = Default[param]
