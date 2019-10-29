import threading
import json
from example import start_parser
from helpers import get_socket
from rcontypes import rcon_event, rcon_receive

playerdict = {}


def callback(event_id, message_string):
    functionarray = []
    for f in functionarray:
        f(event_id, message_string)

if __name__ == "__main__":
    sock = get_socket()
    x = threading.Thread(target = start_parser, args = (sock, callback))
    x.start()
    x.join()