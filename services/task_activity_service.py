from models.taskActivities import TaskActivity
from models.task import Task
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
    if taskActivity == None:
        createTaskActivity(taskId, userId, status) 
    else:
        if status == "correct":
            taskActivity.status = status
            taskActivity.save()
    

def getUserSolvedTasksForSubject(selectedTopics, selectedDifficulties, userId):
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    
    query = Task.select().where(*filters) if filters else Task.select()
    
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
            "topic1": {"solved": X, "total": Y},
            "topic2": {"solved": X, "total": Y}
        }
    }
    """
    user = User.get_or_none(User.name == username)
    if not user:
        return {}
    
    subjects = Task.select(Task.subject).distinct().scalar()
    if not isinstance(subjects, list):
        subjects = [subjects] if subjects else []
    
    data = {}
    
    for subject in subjects:
        if not subject:
            continue
            
        topics = Task.select(Task.topic).where(Task.subject == subject).distinct().scalar()
        if not isinstance(topics, list):
            topics = [topics] if topics else []
        
        subject_data = {}
        
        for topic in topics:
            if not topic:
                continue
                
            stats = getUserSolvedTasksForSubject([topic], [subject], user.id)
            
            subject_data[topic] = {
                "solved": stats["solved"],
                "total": stats["solved"] + stats["unsolved"]
            }
        
        if subject_data:
            data[subject] = subject_data
    
    return data


if not TaskActivity.table_exists():
    TaskActivity.create_table()
    print("Table 'TaskActivity' created")

    