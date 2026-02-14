from peewee import *
from models.base_model import BaseModel

class Duel(BaseModel):
    username1 = CharField()
    username2 = CharField()
    score1 = IntegerField()
    score2 = IntegerField()
    newRating1 = IntegerField()
    newRating2 = IntegerField()
    