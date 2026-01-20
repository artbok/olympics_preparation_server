from peewee import *
from.base_model import BaseModel

class Duel(BaseModel):
    firstUserId = IntegerField()
    secondUserId = IntegerField()
    