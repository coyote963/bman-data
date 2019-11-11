import threading
import json
from example import start_parser
from helpers import get_socket
from rcontypes import rcon_event, rcon_receive
from db_operations import functionarray
from parseconfigs import get_port
from db_svl import svl_functions
from db_dm import dm_functions

def callback_common(event_id, message_string, sock, additional=[]):
    new_functions = functionarray + additional
    for f in new_functions:
        f(event_id, message_string, sock)


def callback_svl(event_id, message_string, sock):
    callback_common(event_id, message_string,sock, additional = svl_functions)

def callback_dm(event_id, message_string, sock):
    callback_common(event_id, message_string, sock, additional = dm_functions)

if __name__ == "__main__":
    gamemodes = ['svl', 'dm', 'tdm', 'ctf']
    threaddict = {}
    for mode in gamemodes:
        sock = get_socket(mode)
        if mode == 'svl':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_svl))
        if mode == 'dm':
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_dm))
        else:
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_common))

    for mode, thread in threaddict.items():
        thread.start()

    for mode, thread in threaddict.items():
        thread.join()