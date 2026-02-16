from models.taskActivities import TaskActivity
from models.user import User

def getTaskActivity(taskId, userId) -> TaskActivity:
    return TaskActivity.get_or_none(TaskActivity.taskId == taskId, TaskActivity.userId == userId)

def createTaskActivity(taskId, userId, status):
    TaskActivity.create(taskId = taskId, userId = userId, status = status)

def countCorrect(userId):
    return len(TaskActivity.select().where(TaskActivity.userId == userId, TaskActivity.status == "correct"))


def countIncorrect(userId):
    return len(TaskActivity.select().where(TaskActivity.userId == userId, TaskActivity.status == "incorrect"))


def bindTaskWithUser(taskId, userId, status):
    taskActivity: TaskActivity = getTaskActivity(taskId, userId)
    user: User = User.get_by_id(userId)
    if taskActivity == None:
        createTaskActivity(taskId, userId, status) 
    else:
        if status == "correct":
            taskActivity.status = status
    
    
if not TaskActivity.table_exists():
    TaskActivity.create_table()
    print("Table 'TaskActivity' created")

    