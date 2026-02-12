from peewee import *
from models.base_model import BaseModel


class User(BaseModel):
    id = AutoField()
    name = CharField()
    password = CharField()
    rightsLevel = IntegerField(default=1)
    rating = IntegerField(default=1000)
    totalTimeInDuels = IntegerField(default=0)
    duelAnswers = IntegerField(default=0)
    ratingChanges = TextField(default="0")