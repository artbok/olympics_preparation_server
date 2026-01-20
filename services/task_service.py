from peewee import *
from models.task import Task


def createTask(subject, topic, difficulty, description, hint):
    Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()