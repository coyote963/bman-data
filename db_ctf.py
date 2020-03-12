from webhook_url import urlctf
from webhook import send_discord
import json
from rcontypes import rcon_event, rcon_receive
from schemas import Player, PlayerAccount, CTFMessage, CTFProfile,CTFScore, CTFRatingInstance, CTFMatch
from update_cache import get_handle_cache
from helpers import send_request
from mongoengine import DoesNotExist
from datetime import datetime
from trueskill import Rating, rate

player_dict = {}
current_match = None


def upsert_player(player):
    """Upserts a ctfprofile given a player"""
    try:
        ctf_profile = CTFProfile.objects.get(player = player)
    except DoesNotExist:
        ctf_profile = CTFProfile(player = player)
    ctf_profile.save()
    return ctf_profile

def get_player(x):
    """Gets a single player from a json packet"""
    try:
        x = json.loads(x)
    except:
        pass
    if 'StoreID' in x:
        store = x['StoreID']
        profile = x['ProfileID']
    else:
        store = x['Store']
        profile = x['Profile']
    player_account = PlayerAccount(
        platform = store,
        profile = profile
    )
    try:
        player = Player.objects.get(profile = player_account)
    except DoesNotExist:
        raise Exception("Can't retrieve player")
    return player

def create_new_match(map_name):
    match = CTFMatch(
        map_name = map_name,
        date_created = datetime.utcnow(),
    )
    match.save()
    return match


def update_score(js):
    """Saved the information for the player that scored into ctf_scores"""
    if current_match is not None:
        print(current_match)
        x = json.loads(js['CarrierProfile'])
        player = get_player(x)
        ctf_player = upsert_player(player)
        ctf_player.update(inc__captures = 1)
        ctf_score = CTFScore(
            player = player,
            ctf_player = ctf_player,
            match = current_match,
            team = js['ScoringTeam']
            )
        ctf_score.save()

def update_ctf_chat(js):
    player = Player.objects.get(profile=player_dict[js["PlayerID"]])
    ctf_player = upsert_player(player)
    ctf_message = CTFMessage(
        message = js["Message"],
        name = js["Name"],
        player = player.id,
        ctf_player = ctf_player.id
    )
    ctf_message.save()

def get_rating_team(team):
    """Expects a list of json packets, returns a list of trueskill rating objects corresponding to the team"""
    result = []
    for p in team:
        p = upsert_player(get_player(p))
        result.append(Rating(mu = p['mu'], sigma = p['sigma']))
    return result

def get_player_team(team):
    """Expects a list of json packets, returns a list of player objects"""
    result = []
    for p in team:
        db_player = get_player(p)
        result.append(db_player)
    return result


def get_db_team(team):
    """Expects a list of json packets, returns a list of ctf_profile database objects"""
    result = []
    for p in team:
        db_player = upsert_player(get_player(p))
        result.append(db_player)
    return result

def update_wins(team_profiles):
    """Expects a list of ctfprofiles, and increments the wins field of all of them"""
    for i in range(0, len(team_profiles)):
        team_profiles[i].update(inc__wins = 1)


def update_losses(team_profiles):
    """Expects a list of ctfprofiles, and increments the losses field of all of them"""
    for i in range(0, len(team_profiles)):
        team_profiles[i].update(inc__losses = 1)

def update_rating_instance(player, ctf_profile, rating, match):
    """Expects player is a player object, rating is a rating object, ctfprofile is a ctf profile"""
    c = CTFRatingInstance(player = player,
        ctf_player = ctf_profile,
        match= match,
        mu = rating.mu,
        sigma = rating.sigma,
        mu_delta = rating.mu - ctf_profile.mu,
        sigma_delta = rating.sigma - ctf_profile.sigma
    )
    c.save()

def update_rating(players, team, ratings):
    """ players is db objects of players, team is an array of db objects of ctf profiles, ratings is rating objects"""
    if len(team) != len(ratings):
        raise Exception("There was an asymmetry in the new ratings")
    else:
        for i in range(0, len(team)):
            update_rating_instance(players[i], team[i], ratings[i], current_match)
            team[i].mu = ratings[i].mu
            team[i].sigma = ratings[i].sigma
            team[i].last_updated = datetime.utcnow()
            team[i].save()

def update_player_rating(usc, man, result):
    """usc and man are rcon dicts"""
    if len(usc) > 0 and len(man) > 0:
        usc_rating = get_rating_team(usc)
        man_rating = get_rating_team(man)
        if result == "1":
            x = rate([usc_rating, man_rating], [0,1])
        else:
            x = rate([usc_rating, man_rating], [1,0])
        new_usc, new_man = x
        db_usc_profiles = get_db_team(usc)
        db_man_profiles = get_db_team(man)
        db_usc_players = get_player_team(usc)
        db_man_players = get_player_team(man)
        update_rating(db_usc_players, db_usc_profiles, new_usc)
        update_rating(db_man_players, db_man_profiles, new_man)
        if result == "1":
            update_wins(db_man_profiles)
            update_losses(db_usc_profiles)
        else:
            update_wins(db_usc_profiles)
            update_losses(db_man_profiles)




def handle_ctf_chat(event_id, message_string, sock):
    if event_id == rcon_event.chat_message.value:
        js = json.loads(message_string)
        if 'PlayerID' in js and js['PlayerID'] != '-1':
            update_ctf_chat(js)
            send_discord(js, urlctf)

def handle_ctf_scored(event_id, message_string, sock):
    """Handles the event of a player scoring"""
    print(current_match)
    print(player_dict)
    if event_id == rcon_event.ctf_scored.value:
        js = json.loads(message_string)
        if js['CarrierID'] in player_dict:
            update_score(js)
            requestID = "scored " + js['ScoringTeam']
            send_request(sock, requestID, requestID, rcon_receive.request_scoreboard.value)

def handle_scoreboard_scored(event_id, message_string, sock):
    """Handles the specific case that a player scores and the requestId is scored"""
    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        global current_match
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            if current_match is None:
                current_match = create_new_match(js['Map'])
            if js['RequestID'].startswith("scored"):
                usc = []
                man = []
                for k in js.keys():
                    if k.startswith('PlayerData') and js[k]['Bot'] != "1":
                        if js[k]['Team'] == '1':
                            usc.append(js[k])
                        if js[k]['Team'] == '2':
                            man.append(js[k])
                print(usc)
                print(man)
                # get the team that scored
                result = js['RequestID'].split(" ")[1]
                update_player_rating(usc, man, result)

def handle_match_end(event_id, message_string, sock):
    if event_id == rcon_event.match_end.value:
        js = json.loads(message_string)
        map_name = js['NextMap']
        global current_match
        current_match = create_new_match(map_name)

def handle_player_death(event_id, message_string, sock):
    if event_id == rcon_event.player_death.value:
        js = json.loads(message_string)
        if js['KillerID'] in player_dict.keys() and js['VictimID'] in player_dict.keys():
            killer_profile = upsert_player(get_player(js['KillerProfile']))
            victim_profile = upsert_player(get_player(js['VictimProfile']))
            killer_profile.update(inc__kills = 1)
            victim_profile.update(inc__deaths = 1)

handle_cache = get_handle_cache(player_dict)

ctf_functions = [
    handle_cache,
    handle_ctf_chat,
    handle_ctf_scored,
    handle_scoreboard_scored,
    handle_match_end,
    handle_player_death
]