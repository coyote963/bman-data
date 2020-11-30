from mongoengine import Document,EmbeddedDocument, EmbeddedDocumentField,ReferenceField, ListField, StringField, DateTimeField, FloatField, IntField, connect, BooleanField
import datetime
from pymongo import MongoClient
import pymongo
from parseconfigs import uri

print(connect(host = uri, db="bmdb"))

class DMMatch(Document):
    map_name = StringField(max_length=40, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'dm_matches'}

class SVLMatch(Document):
    map_name = StringField(max_length=40, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    date_ended = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'svl_matches'}

class CTFMatch(Document):
    map_name = StringField(max_length=40, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'ctf_matches'}



class PlayerAccount(EmbeddedDocument):
    platform = StringField(max_length=2)
    profile = StringField(max_length=40)

class Player(Document):
    profile = EmbeddedDocumentField(PlayerAccount)
    color = StringField(max_length=10, required=True)
    name = ListField(StringField())
    premium = StringField(max_length=1, required=True)
    ip = ListField(StringField())
    hat = StringField(max_length=3)
    clan_id = StringField(required=True)
    clan_tag = StringField(required=True)
    meta = {'collection' : 'players'}


class SVLMessage(Document):
    message = StringField(max_length=200, required=True)
    name = StringField(max_length=50, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    profile = ReferenceField(Player, required=True)
    meta = {'collection' : 'svl_messages'}

class SVLRound(Document):
    wave_number = StringField(max_length=4, required=True)
    enemies = StringField(max_length=4, required=True)
    chests = StringField(max_length=4, required=True)
    chest_price = StringField(max_length=8, required=True)
    capture_progress = StringField(max_length=4, required=True)
    chest_crash = StringField(max_length=4, required=True)
    current_match = ReferenceField(SVLMatch, required=True)
    meta = {'collection' : 'svl_rounds'}



class SVLDeath(Document):
    victim = ReferenceField(Player)
    enemy_rank = StringField(max_length=2, required=True)
    enemy_type = StringField(max_length=2, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    current_round = ReferenceField(SVLRound, required=True)
    weapon = StringField(max_length=3, required=True)
    meta = {'collection' : 'svl_deaths'}

class SVLKill(Document):
    killer = ReferenceField(Player)
    enemy_rank = StringField(max_length=2, required=True)
    enemy_type = StringField(max_length=2, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    current_round = ReferenceField(SVLRound, required=True)
    weapon = StringField(max_length=3, required=True)
    meta = {'collection' : 'svl_kills'}



class DMRatingInstance(EmbeddedDocument):
    mu = FloatField(default=25, required=True)
    sigma = FloatField(default=25.0/3, required=True)
    mu_delta = FloatField()
    sigma_delta = FloatField()



class TDMEloRating(EmbeddedDocument):
    elo = FloatField(required=True)
    delta = FloatField(required=True)






class DMProfile(Document):
    player = ReferenceField(Player, required=True, unique=True)
    mu = FloatField(default=25, required=True)
    sigma = FloatField(default=25.0/3, required=True)
    kills = IntField(default=0, required=True)
    deaths = IntField(default=0, required=True)
    last_updated = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'dm_profiles'}

class CTFProfile(Document):
    player = ReferenceField(Player, required=True, unique=True)
    mu = FloatField(default=25, required=True)
    sigma = FloatField(default=25.0/3, required=True)
    kills = IntField(default=0, required=True)
    deaths = IntField(default=0, required=True)
    wins = IntField(default=0, required=True)
    losses = IntField(default = 0, required=True)
    captures = IntField(default = 0, required=True)
    games = IntField(default = 0, required=True)
    last_updated = DateTimeField(default = datetime.datetime.utcnow())
    meta = {'collection' : 'ctf_profiles'}

class TDMProfile(Document):
    player = ReferenceField(Player, required=True, unique=True)
    mu = FloatField(default=25.0, required=True)
    sigma = FloatField(default=25.0/3, required=True)
    elo = FloatField(default=1000.0, required=True)
    kills = IntField(default=0, required=True)
    deaths = IntField(default = 0, required = True)
    wins = IntField(default = 0, required=True)
    losses = IntField(default = 0, required=True)
    last_updated = DateTimeField(default = datetime.datetime.utcnow())
    meta = {'collection' : 'tdm_profiles'}

class CTFRatingInstance(Document):
    player = ReferenceField(Player, required=True)
    ctf_player = ReferenceField(CTFProfile, required=True)
    match = ReferenceField(CTFMatch, required=True)
    mu = FloatField(default=25, required=True)
    sigma = FloatField(default=25.0/3, required=True)
    mu_delta = FloatField(required=True)
    sigma_delta = FloatField(required=True)
    meta = { 'collection' : 'ctf_rating_instances'}


class DMMessage(Document):
    message = StringField(max_length=200, required=True)
    name = StringField(max_length=50, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    player = ReferenceField(Player, required=True)
    dm_player = ReferenceField(DMProfile, required=True)
    meta = {'collection' : 'dm_messages'}

class TDMMessage(Document):
    message = StringField(max_length=200, required=True)
    name = StringField(max_length=50, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    player = ReferenceField(Player, required=True)
    tdm_player = ReferenceField(TDMProfile, required = False)
    meta = {'collection' : 'tdm_messages'}

class CTFMessage(Document):
    message = StringField(max_length=200, required=True)
    name = StringField(max_length=50, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    player = ReferenceField(Player, required=True)
    ctf_player = ReferenceField(CTFProfile, required = False)
    meta = {'collection' : 'ctf_messages'}

class CTFScore(Document):
    player = ReferenceField(Player, required=True)
    ctf_player = ReferenceField(CTFProfile, required = True)
    match = ReferenceField(CTFMatch, required=True)
    team = StringField(max_field=10, required=True)
    meta = {'collection' : 'ctf_scores'}

# cross referenced
class DMKill(Document):
    killer = ReferenceField(Player, required=True)
    killer_profile = ReferenceField(DMProfile, required=True)
    victim = ReferenceField(Player, required=True)
    victim_profile = ReferenceField(DMProfile, required=True)
    killer_rating = EmbeddedDocumentField(DMRatingInstance, required=True)
    victim_rating = EmbeddedDocumentField(DMRatingInstance, required=True)
    weapon = StringField(max_length=4, required=True)
    killer_location = StringField(max_length=20, required=True)
    victim_location = StringField(max_length=20, required=True)
    date_created = DateTimeField(required=True, default=datetime.datetime.utcnow())
    match = ReferenceField(DMMatch, required=True)
    meta = {'collection' : 'dm_kills'}

# Created a cross reference to the ctf profile
class TDMRound(Document):
    map_name = StringField(max_length=20, required=True)
    man_players = ListField(ReferenceField(Player), required=True)
    usc_players = ListField(ReferenceField(Player), required=True)
    man_players_profiles = ListField(ReferenceField(TDMProfile), required=True)
    usc_players_profiles = ListField(ReferenceField(TDMProfile), required=True)
    result = StringField(max_length=5, required= False)
    created = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'tdm_rounds'}


class TDMKill(Document):
    killer = ReferenceField(Player, required=True)
    victim = ReferenceField(Player, required=True)
    killer_profile = ReferenceField(TDMProfile, required=True)
    victim_profile = ReferenceField(TDMProfile, required=True)
    killer_rating = EmbeddedDocumentField(TDMEloRating, required=True)
    victim_rating = EmbeddedDocumentField(TDMEloRating, required=True)
    weapon = StringField(max_length=4, required=True)
    killer_location = StringField(max_length=20, required=True)
    victim_location = StringField(max_length=20, required=True)
    date_created = DateTimeField(required=True, default=datetime.datetime.utcnow())
    tdm_round = ReferenceField(TDMRound, required=False)
    meta = {'collection' : 'tdm_kills'}

class TDMRatingInstance(Document):
    player = ReferenceField(Player, required = True)
    tdm_player = ReferenceField(TDMProfile, required = True)
    tdm_round = ReferenceField(TDMRound, required = True)
    mu = FloatField(required = True)
    sigma = FloatField(required = True)
    mu_delta = FloatField(required = True)
    sigma_delta = FloatField(required = True)
    meta = { 'collection' : 'tdm_rating_instances' }



class CasinoPlayer(Document):
    player = ReferenceField(Player, required= True)
    balance = IntField(default = 0, required = True)
    daily = IntField(default = 0, required = True)
    last_updated = DateTimeField(default = datetime.datetime.utcnow())
    visibility = BooleanField(default = True, required=True)