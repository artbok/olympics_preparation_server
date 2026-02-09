from peewee import *
from models.base_model import BaseModel


class Task(BaseModel):
    id = AutoField()
    description = CharField()
    solution = CharField(default="")
    hint = CharField(default="")
    answer = CharField()
    difficulty = CharField()
    subject = CharField()
    topic = CharField()
    
    