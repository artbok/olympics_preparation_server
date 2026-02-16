from models.user import User
from services.user_service import getUser
from services.task_activity_service import countCorrect, countIncorrect


def get_user_stats(username):
    user = getUser(username)
    if not user:
        return {"error": "User not found"}
    
    return {
        "username": user.name,
        "rating": user.rating,
        "solved_correctly": countCorrect(user.id),
        "solved_total": countCorrect(user.id) + countIncorrect(user.id)
    }

def get_all_users_stats():
    stats = []
    for user in User.select():
        stats.append({
            "username": user.name,
            "rating": user.rating,
            "solved_correctly": countCorrect(user.id),
            "solved_total": countCorrect(user.id) + countIncorrect(user.id)
        })
    return stats