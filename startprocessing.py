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

def callback_common(event_id, message_string, sock, additional=[]):
    new_functions = functionarray + additional
    #print(new_functions)
    for f in new_functions:
        f(event_id, message_string, sock)


def callback_svl(event_id, message_string, sock):
    callback_common(event_id, message_string,sock, additional=svl_functions)

def callback_dm(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = dm_functions)

def callback_ctf(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = ctf_functions)

def callback_tdm(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = tdm_functions)


if __name__ == "__main__":
    gamemodes = ['tdm', 'dm', 'svl', 'ctf']
    #gamemodes = [ 'ctf']
    threaddict = {}
    for mode in gamemodes:
        sock = get_socket(mode)
        if mode == 'svl':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_svl))
        elif mode == 'dm':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_dm))
        elif mode == 'tdm':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_tdm))
        elif mode == 'ctf':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_ctf))
        else: 
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_common))
    
    for mode, thread in threaddict.items():
        print("started")
        thread.start()
    while True:
        time.sleep(5)
        for mode, thread in threaddict.items():
            if not thread.is_alive():
                print("\n\n\n\n\n\n\n\nCrashed\n\n\n\n\n")
            else:
                print(mode)

    for mode, thread in threaddict.items():
        thread.join()