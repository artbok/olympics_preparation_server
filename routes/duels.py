from flask import Flask, render_template, request, Blueprint
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from datetime import datetime
import asyncio
from services.user_service import getUser
from models.user import User
from models.task import Task
import secrets


duels_bp = Blueprint("duels", __name__)
socketio = SocketIO(cors_allowed_origins="*")


class UserInQueue:
    joinedTime = datetime.now()
    raiting = 1000
    userObj = None
    def __init__(self, user: User):
        self.raiting = user.rating
        self.userObj = user
    

class Player:
    scores = [None, None, None]
    userObj = None
    username = ""
    ready = False
    def __init__(self, user: User):
        self.userObj = user
        self.username = user.name


class Duel:
    duelName = ""
    player1: Player = None
    player2: Player = None
    tasks: list[Task] = []
    index = 0
    roundStartTime = ""
    def __init__(self, duelName, player1, player2):
        self.duelName = duelName
        self.player1 = player1
        self.player2 = player2
        self.tasks = self.generateTasks()

    def getPlayer(self, username: str) -> Player:
        if self.player1.username == username:
            return self.player1
        return self.player2
    
    def generateTasks(self): #To be written
        return []
    

    def startRound(self):
        self.roundStartTime = datetime.now()


    def calculateScore(self, username, correct = True):
        player = self.getPlayer(username)
        score = 0
        if correct:
            #easy 5 min, max: 1000, safe seconds: 50, score = min(k*4, 1000)
            #normal 7.5 min, max: 1500, safe seconds: 75, score = min(k*4, 1500)
            #hard 10 min, max: 2000, safe seconds: 100, score = min(k*4, 2000)
            dif = (datetime.now() - self.roundStartTime).seconds
            match self.tasks[self.index].difficulty:
                case "Простой":
                    score = max(min((300-dif)*4, 1000), 500)
                case "Средний":
                    score = max(min((450-dif)*4, 1500), 750)
                case "Сложный":
                    score = max(min((600-dif)*4, 2000), 1000)
        player.scores[self.index] = score
        return score


duels = {}
userQueue: list[UserInQueue] = []


def eloDiffrence(user1: User, user2: User):
    return abs(user1.rating - user2.rating)




def match_found(player1: User, player2: User):
    duelName = f"Duel{datetime.now().strftime(f"%d-%m-%yT%H:%M:%S:%f|{secrets.token_urlsafe(32)}")}"
    duels[duelName] = Duel(duelName, player1, player2)
    join_room(duelName)
    socketio.emit(f"matchmaking_{player1.name}", {"code": "match_found", "duelName": duelName, "opponent": {"name": player2.name, "rating": player2.rating}})
    socketio.emit(f"matchmaking_{player2.name}", {"code": "match_found", "duelName": duelName, "opponent": {"name": player1.name, "rating": player1.rating}})
    socketio.on_event(duelName, lambda data: handle_duel(duelName, data))



def handle_duel(duelName, data):
    operation = data["operation"]
    username = data["username"]
    duel: Duel = duels[duelName]
    if operation == "answer":
        score = 0
        if duel.tasks[duel.index].answer == data["answer"]:
            score = duel.calculateScore(username)
            socketio.emit(duelName, {"code": "correctAnswer", "roundScore": score, "username": username})
        else:
            score = duel.calculateScore(username, False)
            socketio.emit(duelName, {"code": "wrongAnswer", "roundScore": score, "username": username})

        if duel.player1.scores[duel.index] != None and duel.player2.scores[duel.index] != None:
            pass
        
    elif operation == "join":
        player = duel.getPlayer(username)
        player.ready = True
        if duel.player1.ready and duel.player2.ready:
            socketio.emit(duelName, {"code": "start_duel", "task": duel.tasks[0]})


    
            

@socketio.on("matchmaking")
def handle_matchmaking(username):
    user = getUser(username)
    if len(userQueue) != 0:
        opponent = userQueue[0]
        dif = (datetime.now() - opponent.joinedTime).seconds
        if dif > 30:
            userQueue.pop(0)
            match_found(opponent.userObj, user)
            return
    for userInQueue in userQueue:
        opponent = userInQueue.userObj
        if abs(opponent.rating - user.rating) <= 50:
            userQueue.remove(userInQueue)
            match_found(opponent, user)
            return
    userQueue.append(UserInQueue(user))
    asyncio.run(asyncio.sleep(30))
    if user in userQueue and userQueue > 1:
        bestOpponent = None
        for opponent in userQueue:
            if opponent != user:
                if bestOpponent and eloDiffrence(user, bestOpponent) > eloDiffrence(user, opponent):
                    bestOpponent = opponent
                else:
                    bestOpponent = opponent
        userQueue.remove(user)
        userQueue.remove(bestOpponent)
        match_found(bestOpponent, user)
