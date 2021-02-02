import time
heartbeats = {}

def initialize_heartbeats(gamemodes):
    for mode in gamemodes:
        heartbeats[mode] = time.perf_counter()

def update_heartbeat_creator(gamemode):
    def update_heartbeat():
        heartbeats[gamemode] = time.perf_counter()
    return update_heartbeat