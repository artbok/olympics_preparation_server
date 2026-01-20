from peewee import *
from .base_model import BaseModel   

class TaskActivities(BaseModel):
    id = AutoField()
    taskId = IntegerField()
    userId = IntegerField()
    