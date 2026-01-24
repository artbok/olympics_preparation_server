from peewee import *
from models.base_model import BaseModel

class Duel(BaseModel):
    firstUserId = IntegerField()
    secondUserId = IntegerField()
    