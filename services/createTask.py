from peewee import *
from models.base_model import task


def createTask(subject, topic, difficulty, description, hint):
    task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint)
    
