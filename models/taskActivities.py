from peewee import *
from models.base_model import BaseModel   

class TaskActivities(BaseModel):
    id = AutoField()
    taskId = IntegerField()
    userId = IntegerField()
    status = CharField(default="notSolved")
    