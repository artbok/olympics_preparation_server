from peewee import *
from models.task import Task
from playhouse.shortcuts import model_to_dict


def createTask(subject, topic, difficulty, description, hint, answer):
    Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint, answer = answer)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()



def getTasks(subject, topic, difficulty, description, page) -> list[map]:
    tasks = []
    filters = []
    
    if subject:
        filters.append(Task.subject == subject)
    if topic:
        filters.append(Task.topic == topic)
    if difficulty:
        filters.append(Task.difficulty == difficulty)
    if description:
        filters.append(Task.description == description)
    
    for task in Task.select().where(*filters).paginate(page, 10):
        tasks.append(model_to_dict(task))
    return tasks




if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")
"""
TO BE ADDED
- getTasks(subject, topic, difficulty, description)
      subject, topic, difficulty, description - optional filters
    returns List<Task>
"""

if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")
