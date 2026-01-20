from peewee import *
from .base_model import BaseModel


class Task(BaseModel):
    id = AutoField()
    description = CharField()
    solution = CharField()
    hint = CharField()
    answer = CharField()
    difficulty = CharField()
    subject = CharField()
    topic = CharField()
    
    