from flask import Flask, render_template, request, Blueprint
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from datetime import datetime
from asyncio import sleep
from services.user_service import getUser
from models.user import User


duels_blueprint = Blueprint("duels", __name__)

socketio = SocketIO(duels_blueprint)

class UserInQueue:
    joinedTime = datetime.now()
    raiting = 1000
    userObj = None
    def __init__(self, user: User):
        self.raiting = user.rating
        self.userObj = user 

class Player:
    score = 0
    answerTimes = [-1, -1, -1]
    current_question_index = 0
    userObj = None
    def __init__(self, user: User):
        self.userObj = user


duels = {}
userQueue: list[UserInQueue] = []


def eloDiffrence(user1: User, user2: User):
    return abs(user1.rating - user2.rating)

def generateTasks(): #To be written
    return []


def startDuel(player1: User, player2: User):
    duelName = f"Duel{datetime.now().strftime("%d.%m.%Y | %H:%M:%S:%f")}"
    duels[duelName] = {
        "player1": Player(player1),
        "player2": Player(player2),
        "questions": generateTasks()
    }


@socketio.on("join")
async def handle_join(username):
    user = getUser(username)
    if len(userQueue) != 0:
        opponent = userQueue[0]
        dif = (datetime.now() - opponent.joinedTime).seconds
        if dif > 30:
            userQueue.pop(0)
            startDuel(opponent, user)

    for opponent in userQueue:
        if abs(opponent.rating - user.rating) <= 150:
            userQueue.remove(opponent)
            startDuel(opponent, user)
    userQueue.append(UserInQueue(user))
    await sleep(30)
    if user in userQueue and userQueue > 1:
        bestOpponent = None
        for opponent in userQueue:
            if opponent != user:
                if bestOpponent and eloDiffrence(user, bestOpponent) > eloDiffrence(user, opponent):
                    bestOpponent = opponent
                else:
                    bestOpponent = opponent
        startDuel(bestOpponent, user)
