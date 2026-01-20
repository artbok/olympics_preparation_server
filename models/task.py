from peewee import *
from base_model import BaseModel


class Task(BaseModel):
    id = AutoField()
    description = CharField()
    solution = CharField(default="")
    hint = CharField(default="")
    answer = CharField()
    difficulty = CharField(default="")
    subject = CharField(default="")
    topic = CharField(default="")
    
    