import threading
import json
from example import start_parser
from helpers import get_socket
from rcontypes import rcon_event, rcon_receive
from db_operations import functionarray
from parseconfigs import get_port
from db_svl import svl_functions
from db_dm import dm_functions
from db_tdm import tdm_functions
from db_ctf import ctf_functions
from update_team_cache import team_cache_functions
import time
from schemas import initialize
import logging
from datetime import datetime
from heartbeat import initialize_heartbeats, update_heartbeat_creator
TIMEOUT = 20

logging.basicConfig( filename= "processing.log", format='%(asctime)s %(relativeCreated)6d %(threadName)s %(message)s')

def callback_common(event_id, message_string, sock, additional=[]):

    new_functions = functionarray + additional
    
    for f in new_functions:
        f(event_id, message_string, sock)
    # except Exception as e:
    #     logging.exception("Error Occurred" + str(e))
    # for f in new_functions:
    #     f(event_id, message_string, sock)



def callback_svl(event_id, message_string, sock):
    callback_common(event_id, message_string,sock, additional = svl_functions)

def callback_dm(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = dm_functions)

def callback_ctf(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = ctf_functions)

def callback_tdm(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = tdm_functions)

callback_dict = {
    "svl" : callback_svl,
    "ctf" : callback_ctf,
    "dm" : callback_dm,
    "tdm" : callback_tdm,
}

thread_heartbeats = { }
if __name__ == "__main__":
    gamemodes = [
        'tdm',
        'dm',
        'svl',
        'ctf'
    ]
    #gamemodes = [ 'ctf']
    threaddict = {}
    # wrapped_parser = threadwrap(start_parser)
    initialize()
    initialize_heartbeats(gamemodes)
    for mode in gamemodes:
        sock = get_socket(mode)
        thread_heartbeats[mode] = time.perf_counter()
        threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_dict[mode], update_heartbeat_creator(mode)))
    
    for mode, thread in threaddict.items():
        print("started")
        thread.start()
    while True:
        time.sleep(5)
        running = 0
        for mode in threaddict.keys():
            if not threaddict[mode].is_alive() or time.perf_counter() - thread_heartbeats[mode] > TIMEOUT:
                try:
                    sock = get_socket(mode)
                    threaddict[mode].join()
                    replacement_thread = threading.Thread(target = start_parser, args = (sock, callback_dict[mode], update_heartbeat_creator(mode)))
                    threaddict[mode] = replacement_thread
                    replacement_thread.start()
                except Exception as e:
                    # datetime object containing current date and time
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    print("date and time =", dt_string)	
                    print(e)
                print("restarting " + mode)
                
            else:
                running += 1
        if running != len(gamemodes):
            print(running / len(gamemodes))

    # for mode, thread in threaddict.items():
    #     thread.join()