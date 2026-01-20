from peewee import *
from .base_model import BaseModel


class User(BaseModel):
    id = AutoField()
    name = CharField()
    password = CharField()
    rightsLevel = IntegerField()
    rating = IntegerField()
    totalTime = IntegerField()
    solvedCorrectly = IntegerField()
    solvedIncorrectly = IntegerField()