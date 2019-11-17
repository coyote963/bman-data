from webhook_url import urltdm
from webhook import send_discord
import json
from rcontypes import rcon_event
from schemas import Player, TDMMessage
from update_cache import get_handle_cache

player_dict = {}
def update_tdm_chat(js):
    player = Player.objects.get(profile=player_dict[js["ID"]])
    tdm_message = TDMMessage(
        message = js["Message"],
        name = js["Name"],
        profile = player,
    )
    tdm_message.save()

def handle_tdm_chat(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if js['Profile'] != '-1':
            update_tdm_chat(js)
            send_discord(js, urltdm)

handle_cache = get_handle_cache(player_dict)

tdm_functions = [
    handle_tdm_chat,
    handle_cache
]