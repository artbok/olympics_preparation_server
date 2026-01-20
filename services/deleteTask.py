from peewee import *
from models.base_model import task

def deleteItem(taskId):
    task = task.get(taskId)
    task.delete_instance()