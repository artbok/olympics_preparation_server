from peewee import *
from models.base_model import BaseModel


class User(BaseModel):
    id = AutoField()
    name = CharField()
    password = CharField()
    rightsLevel = IntegerField(default=1)
    rating = IntegerField(default=1000)
    totalTime = IntegerField(default=0)
    solvedCorrectly = IntegerField(default=0)
    solvedIncorrectly = IntegerField(default=0)
    ratingChanges = TextField(default="0")