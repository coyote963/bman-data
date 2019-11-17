from webhook_url import urlctf
from webhook import send_discord
import json
from rcontypes import rcon_event
from schemas import Player, CTFMessage
from update_cache import get_handle_cache

player_dict = {}

def update_ctf_chat(js):
    player = Player.objects.get(profile=player_dict[js["PlayerID"]])
    ctf_message = CTFMessage(
        message = js["Message"],
        name = js["Name"],
        profile = player,
    )
    ctf_message.save()

def handle_ctf_chat(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if 'PlayerID' in js and js['PlayerID'] != '-1':
            update_ctf_chat(js)
            send_discord(js, urlctf)

handle_cache = get_handle_cache(player_dict)

ctf_functions = [
    handle_ctf_chat,
    handle_cache
]