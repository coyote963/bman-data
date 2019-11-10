from helpers import send_request, get_socket
from rcontypes import rcon_receive
sock = get_socket()
send_request(sock, '74.135.19.94', '76561198303147008', rcon_receive.request_player.value)