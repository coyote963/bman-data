from rcontypes import rcon_event, rcon_receive
from datetime import datetime
from helpers import send_request
from db_operations import get_mongo_client
from ratingsystem import perform_trueskill_adjustment
import json

from update_cache import get_handle_cache
from schemas import DMMatch, DMKill, DMMessage, Player, PlayerAccount, DMProfile, DMRatingInstance
requestID = "Coyote"
player_dict = {}
current_match = None
handle_cache = get_handle_cache(player_dict)
db = get_mongo_client()


def update_dm_match(js):
    global current_match
    dm_match = DMMatch(
        map_name = js["Map"]
    )
    dm_match.save()
    current_match = dm_match
    # result = db.dm_matches.insert_one({
    #     "map_name" : js["Map"],
    #     "date_created" : datetime.now()
    # })
    # current_match = result.inserted_id

def update_dm_kills(js):
    killer = PlayerAccount(
        platform = player_dict[js['KillerID']]['platform'],
        profile = player_dict[js['KillerID']]['profile']
    )
    victim = PlayerAccount(
        platform = player_dict[js['VictimID']]['platform'],
        profile = player_dict[js['VictimID']]['profile']
    )
    victim = Player.objects.get(profile=victim)
    killer = Player.objects.get(profile=killer)
    dm_kill = DMKill(
        victim = victim,
        killer = killer,
        weapon = js['KillerWeapon'],
        killer_location = js["KillerX"] + "," + js["KillerY"],
        victim_location = js["VictimX"] + "," + js["VictimY"],
        match = current_match,
    )
    # Perform the rating adjustment, Refactor into a separate func
    try:
        dm_killer_profile = DMProfile.objects.get(player=killer)
    except:
        dm_killer_profile = DMProfile(player=killer)
        dm_killer_profile.save()
    
    try:
        dm_victim_profile = DMProfile.objects.get(player=victim)
    except:
        dm_victim_profile = DMProfile(player=victim)
        dm_victim_profile.save()

    adjustment = perform_trueskill_adjustment(dm_killer_profile, dm_victim_profile)
    killer_rating_instance = DMRatingInstance(mu = adjustment['killer_mu'],
        sigma = adjustment['killer_sigma'],
        mu_delta= adjustment['killer_mu_delta'],
        sigma_delta = adjustment['killer_sigma_delta'])
    victim_rating_instance = DMRatingInstance(mu = adjustment['victim_mu'],
        sigma = adjustment['victim_sigma'],
        mu_delta= adjustment['victim_mu_delta'],
        sigma_delta = adjustment['victim_sigma_delta'])
    dm_kill.killer_rating = killer_rating_instance
    dm_kill.victim_rating = victim_rating_instance
    dm_kill.save()

def update_dm_matchend():
    DMMatch.objects(id = current_match.id).update_one(
        set__date_ended = datetime.utcnow()
    )
    # db.dm_matches.update_one({
    #     '_id' : current_match
    # }, {
    #     '$set' : {
    #         'date_ended' : datetime.now()
    #     }
    # })

def update_dm_chat(js):
    dm_message = DMMessage(
        message = js["Message"],
        name = js["Name"],
        profile = js["Profile"],
    )
    dm_message.save()
    # db.dm_messages.insert_one({
    #     "message" : js["Message"],
    #     "name" : js['Name'],
    #     "profile" : js["Profile"],
    #     "date_created" : datetime.now()
    # })


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
                update_dm_kills(js)
                update_elo_rating(js)

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