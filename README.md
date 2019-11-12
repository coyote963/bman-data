# bman-data
A database that connects to multiple game clients, recording in game events

This is code that connects to 4 game servers in the Video Game: Boring Man 2.0 Rewrite.

It can also be used as a framework for developing tools for other purposes. 

The db used is MongoDB, and ORM is MongoEngine

# Files #

For all files starting with db_, function names starting with "handle" handle socket events, pushing the json packets to the update functions that update the database.

`db_bm.py` This file manages db events. Mainly this file is used for adjusting player ratings with the trueskill rating system, it creates match objects, as well as dm player profiles.

`db_operations` This file is for handling common db operations, that all servers share. These include updating the player objects in the database.

`db_svl` This file handles Survival events. When a player kills a bot or vice versa, this file stores this information. It also records waves with information about that wave.

`db_tdm` in progress. I am planning on using trueskills "n vs m" matchup to adjust the ratings, and create a tdm profile

`example.py` This file handles the logic of parsing packets from the game server and is pretty much the code from spasman's example rcon.

`helpers.py` This file has helper functions related to packets. Getting game packets, sendng packets requests of type 1 or type 2.

`parseconfigs.py` Reads the config file: bmsettings.ini and gets all the variables for importing into python code

`ratingsystem.py` This handles utility functions for adjusting player ratings. The functions here return dicts representing how the rating is adjusted and what the final rating is

`rcontypes.py` handles the packet types that come out of the server. Use rcon_receive to send requests for information from the server

`schemas.py` Defines the database schemas for mongoengine. 

`startprocessing.py` The entry point of the code. Running startprocessing makes python call all your functions that are defined in the db_ files.

`update_cache.py` maintains the validity of the player cache, a lookup table for translating playerIDs to profileID's

# Usage #

`pip install requrements.txt` Install all the dependencies

Define the event handlers in the db_ files, and import them into startprocessing.py. Define a function in startprocessing: callback_X where X is the gamemode abbreviation of the server you are targeting. Then call callback_common with the additional parameter set to your event handlers. 

