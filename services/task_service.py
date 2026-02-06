from peewee import *
from models.task import Task


def createTask(subject, topic, difficulty, description, hint, answer):
    Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint, answer = answer)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()



if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")