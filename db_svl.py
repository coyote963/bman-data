import json
from rcontypes import rcon_event, rcon_receive
from db_operations import get_mongo_client
from datetime import datetime
from helpers import send_request
from db_operations import requestID
from update_cache import get_handle_cache
from schemas import SVLMatch, SVLDeath, SVLKill, SVLRound, PlayerAccount, SVLMessage, Player
from webhook_url import urlsvl
from webhook import send_discord
from mongoengine import DoesNotExist

db = get_mongo_client()
player_dict = {}
enemy_dict = {}
current_match = None
current_round = None

def update_svl_match(js):
    global current_match
    svl_match = SVLMatch(
        map_name = js["Map"]
    )
    svl_match.save()
    current_match = svl_match

def update_svl_round(js):
    if current_match is not None:
        global current_round
        svl_round = SVLRound(
            wave_number = js['WaveNumber'],
            enemies = js['Enemies'],
            chests = js['Chests'],
            chest_price = js['ChestPrice'],
            capture_progress = "0" if 'CaptureProgress' not in js else js['CaptureProgress'],
            chest_crash = js['ChestCrash'],
            current_match = current_match
        )
        svl_round.save()
        current_round = svl_round

def update_svl_matchend():
    SVLMatch.objects(id=current_match.id).update_one(
        set__date_ended = datetime.utcnow()
    )

def update_svl_chat(js):
    x = json.loads(js['Profile'])

    profile = PlayerAccount(
        platform = x['StoreID'],
        profile = x['ProfileID']
    )
    try:
        player = Player.objects.get(profile = profile)
    except DoesNotExist:
        return
    svl_message = SVLMessage(
        message = js['Message'],
        name = js['Name'],
        profile = player
    )
    svl_message.save()


# A player killed a npc
def update_svl_kills(js):
    if js["VictimID"] in enemy_dict and js['KillerID'] in player_dict:
        killer = PlayerAccount(
            platform = player_dict[js['KillerID']]["platform"],
            profile = player_dict[js['KillerID']]["profile"]
        )
        killer = Player.objects.get(profile=killer)
        svlkill = SVLKill(
            killer = killer,
            enemy_rank = enemy_dict[js["VictimID"]]["EnemyRank"],
            enemy_type = enemy_dict[js["VictimID"]]["EnemyType"],
            current_round = current_round,
            weapon = js['KillerWeapon']
        )
        svlkill.save()

def update_svl_deaths(js):
    if js["KillerID"] in enemy_dict and js['VictimID'] in player_dict:
        victim = PlayerAccount(
            platform = player_dict[js['VictimID']]["platform"],
            profile = player_dict[js['VictimID']]["profile"]
        )
        victim = Player.objects.get(profile=victim)
        svlDeath = SVLDeath(
            victim = victim,
            enemy_rank = enemy_dict[js["KillerID"]]["EnemyRank"],
            enemy_type = enemy_dict[js["KillerID"]]["EnemyType"],
            current_round = current_round,
            weapon = js["KillerWeapon"]
        )
        svlDeath.save()

def handle_svl_chat_save(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if 'PlayerID' in js and js['PlayerID'] != '-1':
            update_svl_chat(js)
            send_discord(js, urlsvl)



def handle_svl_scoreboard(event_id, message_string, sock):
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            update_svl_match(js)


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
            enemy_dict[js["PlayerID"]] = enemy

handle_cache = get_handle_cache(player_dict)

svl_functions = [handle_svl_scoreboard,
    handle_svl_new_wave,
    handle_svl_match_end,
    handle_cache,
    handle_svl_chat_save,
    handle_player_spawn,
    handle_player_death,]