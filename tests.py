from db_operations import update_player, update_player_array, update_player_ip

newplayer1 = {
    'Profile' : 1234,
    'IP' : '127.0.0.1',
    'Name' : 'Constanza',
    'Color' : 15179512,
    'Premium' : 1,
    'Hat' : 16,
}


newplayer2 = {
    'Profile' : 1234,
    'IP' : '127.0.0.4',
    'Name' : 'Jerry',
    'Color' : 14449512,
    'Premium' : 0,
    'Hat' : 13,
}


newplayer2 = {
    'Profile' : 1222,
    'RequestID' : '127.0.0.5',
    'Name' : 'Kramer',
    'Color' : 14449512,
    'IP' : '127.0.0.5',
    'Premium' : 0,
    'Hat' : 13,
}

update_player_array(newplayer2)
update_player(newplayer2)
