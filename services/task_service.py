from peewee import *
from models.task import Task
from playhouse.shortcuts import model_to_dict
from math import ceil

def createTask(subject, topic, difficulty, description, hint, answer):
    Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint, answer = answer)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()

def editTask(taskId, taskDescription, taskSubject, taskDifficulty, taskHint, taskAnswer, taskTopic):
    task: Task = Task.get(taskId)
    task.description = taskDescription
    task.subject = taskSubject
    task.difficulty = taskDifficulty
    task.hint = taskHint
    task.answer = taskAnswer
    task.topic = taskTopic
    task.save()


def getTasks(page, selectedTopics, selectedDifficulties) -> list[map]:
    tasks = []
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    query = Task.select().where(*filters).paginate(page, 10) if len(filters) > 0 else Task.select().paginate(page, 10)
    for task in query:
        tasks.append(model_to_dict(task))
    return tasks


def getTopics():
    subjects = Task.select(Task.subject).distinct().scalars()
    data = {}
    for subject in subjects:
        data[subject] = list(Task.select(Task.topic).where(Task.subject == subject).distinct().scalars())
    return data


def countTasksPages():
    return ceil(Task.select().count() / 10)
print(getTopics())

if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")
"""
TO BE ADDED
- getTasks(subject, topic, difficulty, description)
      subject, topic, difficulty, description - optional filters
    returns List<Task>
"""
createTask("Математика", "Сложение чисел", "Простой", "2 + 2 = ?", "Посчитай по пальцам", "4")
createTask("Математика", "Сложение чисел", "Простой", "2 + 3 = ?", "Посчитай по пальцам", "5")
createTask("Математика", "Сложение чисел", "Средний", "4 + 7 = ?", "Подумай", "11")
createTask("Математика", "Сложение чисел", "Средний", "13 + 17 = ?", "Подумай", "30")
createTask("Математика", "Сложение чисел", "Сложный", "102 + 236 = ?", "Подумай", "338")
createTask("Математика", "Вычитание чисел", "Средний", "77 - 35 = ?", "Подумай", "42")


if not Task.table_exists():
    Task.create_table()
    createTask("Математика", "Сложение чисел", "Простой", "2 + 2 = ?", "Посчитай по пальцам", "4")
    createTask("Математика", "Сложение чисел", "Простой", "2 + 3 = ?", "Посчитай по пальцам", "5")
    createTask("Математика", "Сложение чисел", "Средний", "4 + 7 = ?", "Подумай", "11")
    createTask("Математика", "Сложение чисел", "Средний", "13 + 17 = ?", "Подумай", "30")
    createTask("Математика", "Сложение чисел", "Сложный", "102 + 236 = ?", "Подумай", "338")
    createTask("Математика", "Вычитание чисел", "Средний", "77 - 35 = ?", "Подумай", "42")
    print("Table 'Task' created")
