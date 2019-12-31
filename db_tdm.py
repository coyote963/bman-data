from webhook_url import urltdm
from webhook import send_discord
import json
from rcontypes import rcon_event, rcon_receive
from schemas import Player,TDMProfile, TDMMessage, TDMRound, PlayerAccount, TDMKill, TDMEloRating
from mongoengine import DoesNotExist
from update_team_cache import get_handle_team_cache
from update_cache import get_handle_cache
from trueskill import Rating, rate
import datetime
from helpers import send_request
from parseconfigs import k
all_players = {}
man_players = []
usc_players = []
current_map = ""
kills = []
requestID = "coyote"

def update_tdm_kills(tdm_round):
    """Called when a tdm round ends, this updates all the entries in kills missing their round with the current round"""
    print(tdm_round)
    for kill in kills:
        kill.tdm_round = tdm_round
        kill.save()
    kills.clear()

def update_tdm_round(js):
    """Called when a TDM Round ends, records the players on each team as well as the result of the round"""
    global usc_players
    global man_players
    db_usc_players =  db_list_profile(usc_players)
    db_man_players = db_list_profile(man_players)
    tdm_round = TDMRound(
        map_name = current_map,
        result = js["Winner"],
        created = datetime.datetime.utcnow()
    )
    tdm_round.save()
    tdm_round.man_players = db_man_players
    tdm_round.usc_players = db_usc_players
    tdm_round.save()
    return tdm_round

def upsert_player(profile_id):
    """Updates and returns a new TDMProfile Player, if the underlying player object does not exist, returns with an error"""
    print(profile_id)
    player_prof = PlayerAccount(
        platform = profile_id['StoreID'],
        profile = profile_id['ProfileID']
    )
    try:
        db_player = Player.objects.get(profile = player_prof)
    except DoesNotExist:
        raise Exception("The player object associated with this account does not exist:\n{}".format(profile_id))
    try:
        tdm_profile = TDMProfile.objects.get(player = db_player)
    except DoesNotExist:
        tdm_profile = TDMProfile(player = db_player)
    tdm_profile.save()
    return tdm_profile



def db_list(player_list):
    """Takes a list of player profiles and returns a list of TDMProfiles"""
    return_list = []
    for p in player_list:
        db_player = upsert_player(p)
        if db_player is not None:
            return_list.append(db_player)
        else:
            raise Exception("Player not found")
    return return_list

def db_list_profile(player_list):
    """Takes a list of player profiles and returns a list of Player objects"""
    return_list = []
    for p in player_list:
        profile = PlayerAccount(
            platform = p['StoreID'],
            profile = p['ProfileID']
        )
        player = Player.objects.get(profile = profile)
        if player is not None:
            return_list.append(profile)
        else:
            raise Exception("Player not found")
    return return_list

def get_rating(player_profile):
    """Given a TDMPlayer object, returns a Trueskill rating object"""
    return Rating(mu = player_profile.mu, sigma = player_profile.sigma)

def perform_adjustment(winner, loser):
    """Given winning and losing teams of player packet objects,
    Performs a rating adjustment returning the winner and loser's new ratings"""
    winner_rating = list(map(get_rating, winner))
    loser_rating = list(map(get_rating, loser))
    new_winner_rating, new_loser_rating = rate([winner_rating, loser_rating], [0,1])
    return [new_winner_rating, new_loser_rating]

def get_player(js):
    x = json.loads(js)
    player_account = PlayerAccount(
        platform = x['StoreID'],
        profile = x['ProfileID']
    )
    try:
        player = Player.objects.get(profile = player_account)
    except DoesNotExist:
        print("ERROR PLAYER DOES NOT EXIST")
        return
    return player

def record_kill(js, killer, victim, killer_delta, victim_delta):
    """Records the kill in the database. js is the packet, killer, victim is Player object, killer_delta, victim_delta give the rating change. return the TDMKill object"""
    killer_rating = TDMEloRating(elo = killer.elo,
        delta = killer_delta
    )
    victim_rating = TDMEloRating(elo = victim.elo,
        delta = victim_delta
    )
    killer_player = get_player(js['KillerProfile'])
    victim_player = get_player(js['VictimProfile'])
    if 'KillerX' in js and 'KillerY' in js:
        killer_location = js['KillerX'] + "," + js['KillerY']
    else:
        killer_location = "Unknown"
    kill = TDMKill(killer = killer_player,
        victim = victim_player,
        weapon = js["KillerWeapon"],
        killer_rating = killer_rating,
        victim_rating = victim_rating,
        killer_location = killer_location,
        victim_location = js['VictimX'] + "," + js["VictimY"],
    )
    return kill

def perform_elo_adjustment(killer, victim):
    """Performs an elo adjustment as well as updating the database"""
    killer_elo = killer.elo
    victim_elo = victim.elo
    killer_prob = (1.0 / (1.0 + pow(10, ((victim_elo-killer_elo) / 400))))
    victim_prob = (1.0 / (1.0 + pow(10, ((killer_elo-victim_elo) / 400))))
    killer_adjust = int(k) * (1 - killer_prob)
    victim_adjust = int(k) * victim_prob
    killer_new_elo = killer_elo + killer_adjust
    victim_new_elo = victim_elo - victim_adjust
    killer.elo = killer_new_elo
    killer.save()
    victim.elo = victim_new_elo
    victim.save()
    return [killer_adjust, victim_adjust]

def update_database(new_team, db_team, win):
    """Parent function that updates all the players in db_team with their new ratings (stored in new_team). win is a bool whether they won or not"""
    if len(new_team) != len(db_team):
        raise Exception("There is an asymmetry in the new ratings and the players on a team")
    else:
        for i in range(0, len(new_team)):
            db_team[i].mu = new_team[i].mu
            db_team[i].sigma = new_team[i].sigma
            if win:
                db_team[i].wins += 1
            else:
                db_team[i].losses += 1
            db_team[i].last_updated = datetime.datetime.utcnow()
            db_team[i].save()

def update_tdm_rating(result):
    """Parent function that performs an adjustment. updates the database"""
    if len(man_players) > 0 and len(usc_players) > 0:
        usc_team = db_list(usc_players)
        man_team = db_list(man_players)
        if result == "1":
            new_usc_team, new_man_team = perform_adjustment(usc_team, man_team)
        else:
            new_man_team, new_usc_team = perform_adjustment(man_team, usc_team)
        update_database(new_usc_team, usc_team, result == "1")
        update_database(new_man_team, man_team, result == "2")


def update_tdm_chat(js):
    """Updates the database with the new chat info"""
    if js["PlayerID"] in all_players:
        cached = all_players[js["PlayerID"]]
        profile = {  'platform' : cached['platform'], 'profile' : cached['profile']}
        player = Player.objects.get(profile=profile)
        tdm_message = TDMMessage(
            message = js["Message"],
            name = js["Name"],
            profile = player,
        )
        tdm_message.save()

def handle_player_spawn(event_id, message_string, sock):
    """appends the new spawn into the list of the players"""
    if event_id == rcon_event.player_spawn.value:
        print("Adding a player")
        js = json.loads(message_string)
        x = json.loads(js["Profile"])
        if js["Team"] == "1":
            usc_players.append(x)
        if js["Team"] == "2":
            man_players.append(x)

def handle_tdm_chat(event_id, message_string, sock):
    """saves the tdm chat message"""
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if 'Profile' in js and js['Profile'] != '-1':
            update_tdm_chat(js)
            send_discord(js, urltdm)
        print("_______________")
        print(man_players)
        print("_______________")
        print(usc_players)

def handle_tdm_scoreboard(event_id, message_string, sock):
    """new scoreboard entry will update the current_map"""
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            global current_map
            current_map = js["Map"]



def handle_tdm_kill(event_id, message_string, sock):
    """handles the case where a kill occurs in a tdm server"""
    if event_id == rcon_event.player_death.value:
        js = json.loads(message_string)
        k = json.loads(js["KillerProfile"])
        v = json.loads(js["VictimProfile"])
        if k['StoreID'] != "-1" and v['StoreID'] != "-1":
            killer = upsert_player(k)
            victim = upsert_player(v)
            killer_delta, victim_delta = perform_elo_adjustment(killer, victim)
            kill = record_kill(js, killer, victim, killer_delta, victim_delta)
            kills.append(kill)
            killer.kills += 1
            victim.deaths += 1
            killer.save()
            victim.save()

def handle_tdm_match(event_id, message_string, sock):
    """handles when a match is over. in this case it requests a scoreboard from the server"""
    if event_id == rcon_event.match_end.value:
        send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

def handle_tdm_round(event_id, message_string, sock):
    """if it is a new round, clear the players on each team and calls to update the database"""
    if event_id == rcon_event.tdm_round_end.value:
        if len(man_players) > 0 and len(usc_players) > 0:
            js = json.loads(message_string)
            tdm_round = update_tdm_round(js)
            update_tdm_rating(js["Winner"])
            update_tdm_kills(tdm_round)
            usc_players.clear()
            man_players.clear()


handle_all_cache = get_handle_cache(all_players)
tdm_functions = [
    handle_all_cache,
    handle_tdm_chat,
    handle_player_spawn,
    handle_tdm_round,
    handle_tdm_scoreboard,
    handle_tdm_kill
]
