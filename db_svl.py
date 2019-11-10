import json
from rcontypes import rcon_event, rcon_receive
from db_operations import get_mongo_client
from datetime import datetime
from helpers import send_request
from db_operations import requestID
db = get_mongo_client()

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

def handle_svl_scoreboard(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            update_svl_match(js)

def handle_svl_new_wave(event_id, message_string, sock):
    if event_id == rcon_event.survival_new_wave.value:
        js = json.loads(message_string)
        update_svl_round(js)

def handle_svl_match_end(event_id, message_string, sock):
    if event_id == rcon_event.match_end.value:
        update_svl_matchend()
        send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

svl_functions = [handle_svl_scoreboard,
    handle_svl_new_wave,
    handle_svl_match_end]