from rcontypes import rcon_event, rcon_receive
import json

# Adds the player into the playerdict, with playerprofile, and team
def handle_scoreboard(event_id, message_string, player_dict):

    if event_id == rcon_event.request_data.value:
        js = json.loads(message_string)
        if int(js['CaseID']) == rcon_receive.request_scoreboard.value:
            for k in js.keys():
                if k.startswith('PlayerData') and js[k]['Bot'] != "1":
                    player_dict[js[k]['ID']] = {
                        'profile' : js[k]["Profile"],
                        'platform' : js[k]['Store'],
                        'team' : js[k]['Team'],
                        'name' : js[k]['Name']
                    }

def handle_spawn(event_id, message_string, player_dict):
    if event_id == rcon_event.player_spawn.value:
        js = json.loads(message_string)
        x = json.loads(js['Profile'])
        if x['ProfileID'] != '-1':
            player_dict[js['PlayerID']] = {
                'profile' : x['ProfileID'],
                'platform' : x['StoreID'],
                'team' : js['Team'],
                'name' : js['Name']
            }
def handle_player_loaded(event_id, message_string, player_dict):
    if event_id == rcon_event.player_loaded.value:
        js = json.loads(message_string)
        x = json.loads(js['Profile'])
        player_dict[js['PlayerID']] = { 'profile': x['ProfileID'], 'platform' : x['StoreID']}

def handle_player_team_change(event_id, message_string, player_dict):
    if event_id == rcon_event.player_team_change.value:
        js = json.loads(message_string)
        x = json.loads(js['Profile'])
        if x['ProfileID'] != '-1':
            player_dict[js['PlayerID']]['team'] = js['NewTeam']

# Clears the data when a round ends
def handle_round(event_id, message_string, player_dict):
    if event_id == rcon_event.tdm_round_end.value:
        print("clearingCLFKJELFKEJLFKJs")
        player_dict.clear()


# team cache functions

team_cache_functions = [handle_spawn, handle_scoreboard, handle_round, handle_player_team_change, handle_player_loaded]

# function that binds the playerdict to the methods
def get_handle_team_cache(player_dict):
    def x(event_id, message_string, sock):
        for f in team_cache_functions:
            f(event_id, message_string, player_dict)
    return x