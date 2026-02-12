from peewee import *
from models.base_model import BaseModel   

class TaskActivity(BaseModel):
    id = AutoField()
    taskId = IntegerField()
    userId = IntegerField()
    status = CharField()