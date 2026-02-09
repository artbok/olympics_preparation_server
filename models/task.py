from peewee import *
from models.base_model import BaseModel


class Task(BaseModel):
    id = AutoField()
    description = CharField()
    solution = CharField(default="")
    hint = CharField(default="")
    answer = CharField()
    explanation = CharField(default="")
    difficulty = CharField(default="")
    subject = CharField(default="")
    topic = CharField(default="")
    
    