import bucchi_automata
import network_simulator as sim
import network_lib as N

SAFETY = "S"
LIVENESS = "L"
safety_automata = None
liveness_automata = None
main_automata = None

def load_safety_automata():
    global safety_automata
    safety_automata = bucchi_automata.decompose_safety(main_automata)
    main_automata.remove_callbacks()


def load_livenes_automata():
    global liveness_automata
    res = bucchi_automata.decompose_liveness(main_automata)
    if res[0] == 1:
        liveness_automata = [res[1]]
        main_automata.remove_callbacks()
    else:
        liveness_automata = [main_automata, res[1]]


def explore_all_paths(network_files, node_id_A, node_id_B, property=SAFETY, automata=None, reset_cb=None):
    global main_automata
    main_automata=automata
    sim.EXPLORE_ALL_PATHS = True
    if property == SAFETY: return verify_safety_between_two_nodes(network_files[0], node_id_A, node_id_B)
    else: return verify_liveness_between_two_nodes(network_files, node_id_A, node_id_B, reset_cb)

loaded = False
Networks = {}
def verify_safety_between_two_nodes(network_file, node_id_A, node_id_B):
    if safety_automata is None:
        load_safety_automata()
    else:
        safety_automata.reset()
    if network_file not in Networks:
        Networks[network_file] = sim.Network(network_file)

    network = Networks[network_file]
    try:
        network.server_send(node_id_A, node_id_B)
    except Exception as e:
        print("Safety Property Failed --", e)
        return False

    for node_id in safety_automata.current_nodes:
        if not safety_automata.all_nodes[node_id].is_accepting:
            print("Safety Property Failed!")
            return False

    safety_automata.current_nodes = [safety_automata.start_node]
    N.reset_vals()
    return True
    # print("Safety Property Holds")
    # safety_automata.remove_callbacks()

def verify_liveness_between_two_nodes(network_file_list, node_id_A, node_id_B, reset_cb):
    good_thing = False
    all_trap = True
    x=0
    for network_file in network_file_list:
        x+=1
        if liveness_automata is None:
            load_livenes_automata()
        else:
            for auto in liveness_automata:
                auto.reset()

        N.reset_vals()
        reset_cb()
        if network_file not in Networks:
            Networks[network_file] = sim.Network(network_file)
        network = Networks[network_file]
        try:
            network.server_send(node_id_A, node_id_B)
        except Exception as e:
            print("Liveness Property Error -- there should be no -- ", e)
            return False

        for auto in liveness_automata:
            for final_state in auto.current_nodes:
                if auto.all_nodes[final_state].is_accepting:
                    good_thing = True
                    if not auto.all_nodes[final_state].is_trap:
                        all_trap = False
                        break

    if good_thing:
        if all_trap:
            print("Liveness Property could not be verified within bounds")
            return False
        else:
            return True
    else:
        print("Liveness property failed")
        return False



