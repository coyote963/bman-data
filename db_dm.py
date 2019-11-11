from rcontypes import rcon_event, rcon_receive
from datetime import datetime
from helpers import send_request
from db_operations import get_mongo_client
import json
from update_cache import get_handle_cache

requestID = "Coyote"
player_dict = {}
current_match = None
handle_cache = get_handle_cache(player_dict)
db = get_mongo_client()


def update_dm_match(js):
    global current_match
    result = db.dm_matches.insert_one({
        "map_name" : js["Map"],
        "date_created" : datetime.now()
    })
    current_match = result.inserted_id

def update_dm_kills(js):
    db.dm_kills.insert_one({
        "victim" : player_dict[js["VictimID"]],
        "killer" : player_dict[js["KillerID"]],
        "weapon" : js["KillerWeapon"],
        "killer_location" : js["KillerX"] + "," + js["KillerY"],
        "victim_location" : js["VictimX"] + "," + js["VictimY"],
        "date_created" : datetime.now(),
        "match" : current_match
    })

def update_dm_matchend():
    db.dm_matches.update_one({
        '_id' : current_match
    }, {
        '$set' : {
            'date_ended' : datetime.now()
        }
    })


def update_dm_chat(js):
    db.dm_messages.insert_one({
        "message" : js["Message"],
        "name" : js['Name'],
        "profile" : js["Profile"],
        "date_created" : datetime.now()
    })


def handle_dm_match_end(event_id, message_string, sock):
    if event_id == rcon_event.match_end.value:
        global current_round
        update_dm_matchend()
        current_round = None
        send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

def handle_dm_chat(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if js['Profile'] != '-1':
            update_dm_chat(js)

def handle_player_death(event_id, message_string, sock):
    if event_id == rcon_event.player_death.value:
        if current_match is not None:
            js = json.loads(message_string)
            if js['KillerID'] in player_dict.keys() and js['VictimID'] in player_dict.keys():
                print("PLAYER KILLED PLAYER")
                update_dm_kills(js)

def handle_dm_scoreboard(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            update_dm_match(js)

dm_functions = [handle_dm_chat,
    handle_cache,
    handle_dm_scoreboard,
    handle_player_death,
    handle_dm_match_end
    ]