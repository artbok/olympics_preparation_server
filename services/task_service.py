from peewee import *
from models.task import Task
from playhouse.shortcuts import model_to_dict
from math import ceil
from services.task_activity_service import getTaskActivity

def createTask(subject, topic, difficulty, description, hint, answer, explanation):
    return Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint, answer = answer, explanation = explanation)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()

def editTask(taskId, taskDescription, taskSubject, taskDifficulty, taskHint, taskAnswer, taskExplanation, taskTopic):
    task: Task = Task.get(taskId)
    task.description = taskDescription
    task.subject = taskSubject
    task.difficulty = taskDifficulty
    task.hint = taskHint
    task.answer = taskAnswer
    task.explanation = taskExplanation
    task.topic = taskTopic
    task.save()


def getTasks(page, selectedTopics, selectedDifficulties, userId=None) -> list[map]:
    tasks = []
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    query = Task.select().where(*filters).paginate(page, 10) if len(filters) > 0 else Task.select().paginate(page, 10)
    for task in query:
        d = model_to_dict(task)
        if userId:
            taskActivity = getTaskActivity(task.id, userId)
            if taskActivity != None:
                if taskActivity.status == "correct":
                    d["status"] = "Решено правильно"
                else:
                    d["status"] = "Решено неправильно"
        tasks.append(d)
    return tasks


def getTopics():
    subjects = Task.select(Task.subject).distinct().scalars()
    data = {}
    for subject in subjects:
        data[subject] = list(Task.select(Task.topic).where(Task.subject == subject).distinct().scalars())
    return data


def countTasksPages(selectedTopics, selectedDifficulties):
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    return ceil(Task.select().where(*filters).count() / 10)



if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")

createTask("Математика", "Сложение чисел", "Простой", "2 + 2 = ?", "Посчитай по пальцам", "4", "Открой калькулятор")
createTask("Математика", "Сложение чисел", "Простой", "2 + 3 = ?", "Посчитай по пальцам", "5", "Открой калькулятор")
createTask("Математика", "Сложение чисел", "Средний", "4 + 7 = ?", "Подумай", "11", "Открой калькулятор")
createTask("Математика", "Сложение чисел", "Средний", "13 + 17 = ?", "Подумай", "30", "Открой калькулятор")
createTask("Математика", "Сложение чисел", "Сложный", "102 + 236 = ?", "Подумай", "338", "Открой калькулятор")
createTask("Математика", "Вычитание чисел", "Средний", "77 - 35 = ?", "Подумай", "42", "Открой калькулятор")


if not Task.table_exists():
    Task.create_table()
    createTask("Математика", "Сложение чисел", "Простой", "2 + 2 = ?", "Посчитай по пальцам", "4", "Открой калькулятор")
    createTask("Математика", "Сложение чисел", "Простой", "2 + 3 = ?", "Посчитай по пальцам", "5", "Открой калькулятор")
    createTask("Математика", "Сложение чисел", "Средний", "4 + 7 = ?", "Подумай", "11", "Открой калькулятор")
    createTask("Математика", "Сложение чисел", "Средний", "13 + 17 = ?", "Подумай", "30", "Открой калькулятор")
    createTask("Математика", "Сложение чисел", "Сложный", "102 + 236 = ?", "Подумай", "338", "Открой калькулятор")
    createTask("Математика", "Вычитание чисел", "Средний", "77 - 35 = ?", "Подумай", "42", "Открой калькулятор")
    print("Table 'Task' created")
