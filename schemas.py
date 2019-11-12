from mongoengine import Document,EmbeddedDocument, EmbeddedDocumentField,ReferenceField, ListField, StringField, DateTimeField, FloatField, IntField, connect
import datetime
from pymongo import MongoClient
import pymongo
from parseconfigs import uri


class DMMatch(Document):
    map_name = StringField(max_length=40, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    date_ended = DateTimeField()
    meta = {'collection' : 'dm_matches'}

class SVLMatch(Document):
    map_name = StringField(max_length=40, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    date_ended = DateTimeField(default=datetime.datetime.utcnow())
    meta = {'collection' : 'svl_matches'}

class PlayerAccount(EmbeddedDocument):
    platform = StringField(max_length=2)
    profile = StringField(max_length=40)

class Player(Document):
    profile = EmbeddedDocumentField(PlayerAccount, primary_key=True)
    color = StringField(max_length=10, required=True)
    name = ListField(StringField())
    premium = StringField(max_length=1, required=True)
    ip = ListField(StringField())
    hat = StringField(max_length=3)
    meta = {'collection' : 'players'}

class DMMessage(Document):
    message = StringField(max_length=200, required=True)
    name = StringField(max_length=50, required=True)
    date_created = DateTimeField(default=datetime.datetime.utcnow())
    profile = ReferenceField(Player, required=True)
    meta = {'collection' : 'dm_messages'}


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
    chest_price = StringField(max_length=4, required=True)
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

    mu_delta = FloatField()
    sigma_delta = FloatField()

class DMKill(Document):
    killer = ReferenceField(Player, required=True)
    victim = ReferenceField(Player, required=True)
    killer_rating = EmbeddedDocumentField(DMRatingInstance, required=True)
    victim_rating = EmbeddedDocumentField(DMRatingInstance, required=True)
    weapon = StringField(max_length=4, required=True)
    killer_location = StringField(max_length=15, required=True)
    victim_location = StringField(max_length=15, required=True)
    date_created = DateTimeField(required=True, default=datetime.datetime.utcnow())
    match = ReferenceField(DMMatch, required=True)
    meta = {'collection' : 'dm_kills'}

class DMProfile(Document):
    player = ReferenceField(Player, required=True, primary_key=True)
    mu = FloatField(default=25, required=True)
    sigma = FloatField(default=default_sigma, required=True)
    kills = IntField(default=0, required=True)
    deaths = IntField(default=0, required=True)
    meta = {'collection' : 'dm_profiles'}
