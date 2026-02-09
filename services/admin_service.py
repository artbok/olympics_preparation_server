from models.user import User
from services.user_service import getUser

def get_user_stats(username):
    user = getUser(username)
    if not user:
        return {"error": "User not found"}
    
    return {
        "username": user.name,
        "rating": user.rating,
        "solved_correctly": user.solvedCorrectly,
        "solved_total": user.solvedCorrectly + user.solvedIncorrectly
    }

def get_all_users_stats():
    stats = []
    for user in User.select():
        stats.append({
            "username": user.name,
            "rating": user.rating,
            "solved_correctly": user.solvedCorrectly,
            "solved_total": user.solvedCorrectly + user.solvedIncorrectly
        })
    return stats