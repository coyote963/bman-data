import json
from rcontypes import rcon_event, rcon_receive
from parseconfigs import uri
from pymongo import MongoClient
from helpers import get_socket, send_request
from schemas import Player, PlayerAccount
requestID = "1"


# initialize some global vars
player_dict = {}

def get_mongo_client():
    mc = MongoClient(uri)
    print("Connected to Mongo DB")
    return mc.bmdb
    
db = get_mongo_client()

# Updates the list of IP's for user JS
# This should only be used to process player join events, and leave
def update_player_array(js):
    x = json.loads(js['Profile'])
    profile = PlayerAccount(
        platform = x['StoreID'],
        profile = x['ProfileID']
    )
    Player.objects(profile=profile).update_one(
        add_to_set__ip=js['IP'],
    )

# Handles a scoreboard event or a request player event, which is executed initially when the script is first run
def update_player(js):
    profile = PlayerAccount(
        platform = js['Store'],
        profile = js['Profile']
    )
    if 'IP' not in js:
        Player.objects(profile=profile).update_one(
            set__color=js['Color'],
            set__premium=js['Premium'],
            add_to_set__name=js['Name'],
            set__hat = js['Hat'],
            upsert=True
        )
    else:
        Player.objects(profile=profile).update_one(
            set__color=js['Color'],
            set__premium=js['Premium'],
            add_to_set__name=js['Name'],
            add_to_set__ip=js['IP'],
            set__hat = js['Hat'],
            upsert=True
        )

# handles the request_player data request event
# This event processes any times the player info packet is received
# Upserts the players if they don't already exists
def handle_request_player(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_player.value:
            if js['RequestID'] != "none":
                # request id must contain the ip address
                js['IP'] = js['RequestID']
            if int(js['CaseID']) == rcon_receive.request_player.value and js['Bot'] == "0":
                update_player(js)

# handles the player logged in rcon event
def handle_rcon_login(event_id, message_string, sock):
    if event_id == rcon_event.rcon_logged_in.value:
        # Issue an rcon request for more information
        requestID = "none"
        # using the RequestID twice because I'm not sure what the second param is for
        # get the current context
        send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

# reset scoreboard
def reset_scoreboard(sock):
    send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

# handles the scoreboard event
def handle_rcon_scoreboard(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            for k in js.keys():
                if k.startswith('PlayerData') and js[k]['Bot'] != "1":
                    #k is the playerindex of a human
                    update_player(js[k])
                    player_dict[js[k]['ID']] = {
                        "platform" : js[k]["Store"],
                        "profile" : js[k]['Profile']
                    }

# handles the player join event
# always asks for additional info from the server, and also updates the database of new IPs
def handle_join(event_id, message_string, sock):
    if event_id == rcon_event.player_connect.value:
        # send a player info request out
        js = json.loads(message_string)
        #update_player_array(js)
        # send a request for additional info, the requestID contains the IP Address
        send_request(sock, js['IP'], js['PlayerID'], rcon_receive.request_player.value)
        player_dict[js['PlayerID']] = {
            "platform" : js["Store"],
            "profile" : js['Profile']
        }

def handle_disconnect(event_id, message_string, sock):
    if event_id == rcon_event.player_disconnect.value:
        js = json.loads(message_string)
        update_player_array(js)

functionarray = [handle_rcon_login,
    handle_rcon_scoreboard,
    handle_join,
    handle_request_player,
    handle_disconnect]