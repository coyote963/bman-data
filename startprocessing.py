import threading
import json
from example import start_parser
from helpers import get_socket
from rcontypes import rcon_event, rcon_receive
from db_operations import handle_rcon_login, handle_rcon_scoreboard, handle_join, handle_request_player, handle_disconnect
from parseconfigs import get_port
from db_svl import svl_functions
playerdict = {}


def callback_common(event_id, message_string, sock, additional=[]):
    functionarray = [handle_rcon_login,
        handle_rcon_scoreboard,
        handle_join,
        handle_request_player,
        handle_disconnect]
    functionarray.extend(additional)
    for f in functionarray:
        f(event_id, message_string, sock)

def callback_svl(event_id, message_string, sock):
    callback_common(event_id,message_string,sock, additional = svl_functions)


if __name__ == "__main__":
    gamemodes = ['svl', 'dm', 'tdm', 'ctf']
    threaddict = {}
    for mode in gamemodes:
        sock = get_socket(mode)
        if mode == "svl":
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_svl))
        else:
            threaddict[mode] = threading.Thread(target = start_parser, args = (sock, callback_common))

    for mode, thread in threaddict.items():
        thread.start()

    for mode, thread in threaddict.items():
        thread.join()