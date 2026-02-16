from models.taskActivities import TaskActivity
from models.user import User
from models.task import Task
from playhouse.shortcuts import model_to_dict

def getTaskActivity(taskId, userId) -> TaskActivity:
    return TaskActivity.get_or_none(TaskActivity.taskId == taskId, TaskActivity.userId == userId)

def getUserSolvedTasksForSubject(selectedTopics, selectedSubjects, userId):
    filters = []
    
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    
    if selectedSubjects and len(selectedSubjects) > 0:
        filters.append(Task.subject << selectedSubjects)
    
    if filters:
        query = Task.select().where(*filters)
    else:
        query = Task.select()
    
    solved = 0
    unsolved = 0
    
    for task in query:
        taskActivity = getTaskActivity(task.id, userId)
        if taskActivity and taskActivity.status == "correct":
            solved += 1
        else:
            unsolved += 1
    
    return {"solved": solved, "unsolved": unsolved}


def getUserTopicsStats(username):
    """
    {
        "subject1": {
            "topic1": {"solved": , "total": },
            "topic2": {"solved": , "total": }
        }
    }
    """
    user = User.get_or_none(User.name == username)
    if not user:
        return {}
    
    subjects = Task.select(Task.subject).distinct().scalars()
    subjects_list = list(subjects) if subjects else []
    
    data = {}
    
    for subject in subjects_list:
        if not subject:
            continue
        
        topics_query = Task.select(Task.topic).where(Task.subject == subject).distinct()
        topics = list(topics_query.scalars())
        
        subject_data = {}
        
        for topic in topics:
            if not topic:
                continue
            
            total_tasks = Task.select().where(
                (Task.subject == subject) & 
                (Task.topic == topic)
            ).count()
            
            solved_tasks = Task.select().join(
                TaskActivity, on=(Task.id == TaskActivity.taskId)
            ).where(
                (Task.subject == subject) & 
                (Task.topic == topic) &
                (TaskActivity.userId == user.id) &
                (TaskActivity.status == "correct")
            ).count()
            
            
            subject_data[topic] = {
                "solved": solved_tasks,
                "total": total_tasks
            }
        
        if subject_data:
            data[subject] = subject_data
    
    return data




def createTaskActivity(taskId, userId, status):
    TaskActivity.create(taskId = taskId, userId = userId, status = status)

def countCorrect(userId):
    return len(TaskActivity.select().where(TaskActivity.userId == userId, TaskActivity.status == "correct"))


def countIncorrect(userId):
    return len(TaskActivity.select().where(TaskActivity.userId == userId, TaskActivity.status == "incorrect"))


def bindTaskWithUser(taskId, userId, status):
    taskActivity: TaskActivity = getTaskActivity(taskId, userId)
    if taskActivity == None:
        createTaskActivity(taskId, userId, status) 
    else:
        if status == "correct":
            taskActivity.status = status
            taskActivity.save()
    
    
if not TaskActivity.table_exists():
    TaskActivity.create_table()

    