import json
from rcontypes import rcon_event, rcon_receive
from db_operations import get_mongo_client
from datetime import datetime
from helpers import send_request
from db_operations import requestID
from update_cache import get_handle_cache

db = get_mongo_client()
player_dict = {}
enemy_dict = {}
current_match = None
current_round = None

def update_svl_match(js):
    global current_match
    result = db.svl_matches.insert_one({
        "map_name" : js["Map"],
        "date_created" : datetime.now(),
        "date_ended" : datetime.now()
    })
    current_match = result.inserted_id

def update_svl_round(js):
    if current_match is not None:
        global current_round
        result = db.svl_rounds.insert_one({
            "wave_number" : js['WaveNumber'],
            "enemies" : js['Enemies'],
            "chests" : js['Chests'],
            "chest_price" : js['ChestPrice'],
            "capture_progress" : js['CaptureProgress'],
            "chest_crash" : js['ChestCrash'],
            "current_match" : current_match
        })
        current_round = result.inserted_id

def update_svl_matchend():
    db.svl_matches.update_one({
        '_id' : current_match
    }, {
        '$set' : {
            'date_ended' : datetime.now()
        }
    })

def update_svl_chat(js):
    db.svl_messages.insert_one({
        "message" : js["Message"],
        "name" : js['Name'],
        "profile" : js["Profile"],
        "date_created" : datetime.now()
    })



def update_svl_kills(js):
        if js["VictimID"] in enemy_dict:
            db.svl_kills.insert_one({
                "killer" : player_dict[js["KillerID"]],
                "enemy_rank" : enemy_dict[js["VictimID"]]["EnemyRank"],
                "enemy_type" : enemy_dict[js["VictimID"]]["EnemyType"],
                "date_created" : datetime.now(),
                "round" : current_round
            })

def update_svl_deaths(js):
    if js["KillerID"] in enemy_dict:
        db.svl_deaths.insert_one({
            "victim" : player_dict[js["VictimID"]],
            "enemy_rank" : enemy_dict[js["KillerID"]]["EnemyRank"],
            "enemy_type" : enemy_dict[js["KillerID"]]["EnemyType"],
            "date_created" : datetime.now(),
            "round" : current_round
        })

def handle_svl_chat(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if js['Profile'] != '-1':
            update_svl_chat(js)

def handle_svl_scoreboard(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            update_svl_match(js)
            for k in js.keys():
                if k.startswith('PlayerData') and js[k]['Bot'] != "1":
                    player_dict[js[k]['ID']] = js[k]['Profile']

def handle_svl_new_wave(event_id, message_string, sock):
    if event_id == rcon_event.survival_new_wave.value:
        js = json.loads(message_string)
        update_svl_round(js)
        enemy_dict.clear()

def handle_svl_match_end(event_id, message_string, sock):
    if event_id == rcon_event.match_end.value:
        global current_round
        update_svl_matchend()
        current_round = None
        send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

def handle_player_death(event_id, message_string, sock):
    if event_id == rcon_event.player_death.value:
        if current_round is not None:
            js = json.loads(message_string)
            if js["VictimID"] in enemy_dict:
                print("Killed a bot lol")
                update_svl_kills(js)
            else:
                update_svl_deaths(js)


def handle_player_spawn(event_id, message_string, sock):
    if event_id == rcon_event.player_spawn.value:
        
        js = json.loads(message_string)
        if "EnemyType" in js: 
            enemy = {
                "EnemyType" : js["EnemyType"],
                "EnemyRank" : js["EnemyRank"]
            }
            global enemy_dict
            enemy_dict[js["PlayerID"]] = enemy

handle_cache = get_handle_cache(player_dict)

svl_functions = [handle_svl_scoreboard,
    handle_svl_new_wave,
    handle_svl_match_end,
    handle_cache,
    handle_svl_chat,
    handle_player_spawn,
    handle_player_death]