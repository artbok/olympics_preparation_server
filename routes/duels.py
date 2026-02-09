from flask import Blueprint
from flask_socketio import SocketIO, emit
from datetime import datetime
import secrets
from peewee import fn

from services.user_service import getUser, updateUserRating
from models.user import User
from models.task import Task


duels_bp = Blueprint("duels", __name__)
socketio = SocketIO(cors_allowed_origins="*")


class UserInQueue:
    def __init__(self, user: User):
        self.joinedTime = datetime.now()
        self.rating = user.rating
        self.userObj = user

class Player:
    def __init__(self, user: User):
        self.scores = [None, None, None]
        self.ready = False
        self.userObj = user
        self.username = user.name
        self.total_score = 0

class Duel:
    def __init__(self, duelName, user1, user2):
        self.index = -1
        self.roundStartTime = None
        self.roundDuration = 0
        self.duelName = duelName
        self.player1 = Player(user1)
        self.player2 = Player(user2)
        self.tasks = self.generateTasks()
        self.finished = False

    def getPlayer(self, username: str) -> Player:
        if self.player1.username == username:
            return self.player1
        return self.player2
    
    def generateTasks(self):
        try:
            easy = Task.select().where(Task.difficulty == "Простой").order_by(fn.Random()).first()
            normal = Task.select().where(Task.difficulty == "Средний").order_by(fn.Random()).first()
            hard = Task.select().where(Task.difficulty == "Сложный").order_by(fn.Random()).first()
            
            if not easy: easy = Task.select().order_by(fn.Random()).first()
            if not normal: normal = Task.select().order_by(fn.Random()).first()
            if not hard: hard = Task.select().order_by(fn.Random()).first()
            return [easy, normal, hard]
        except:
            return []


    def startRound(self):
        self.roundStartTime = datetime.now()


    def calculateScore(self, username, correct=True):
        player = self.getPlayer(username)
        if not correct:
            player.scores[self.index] = 0
            return 0
        
        if self.roundStartTime is None:
            return 0
            
        dif = (datetime.now() - self.roundStartTime).total_seconds()
        
        score = 0
        difficulty = self.tasks[self.index].difficulty
        
        if difficulty == "Простой":
            score = max(min((60 - dif) * 20, 1000), 500)
        elif difficulty == "Средний":
            score = max(min((90 - dif) * 20, 1500), 750)
        elif difficulty == "Сложный":
            score = max(min((120 - dif) * 20, 2000), 1000)
            
        player.scores[self.index] = int(score)
        player.total_score += int(score)
        return int(score)

duels = {}
userQueue: list[UserInQueue] = []


  

def calculateRatings(ratingA, ratingB, score):
  DENOMINATOR = 400
  K = 32

  expectedA = 1 / (1 + pow(10, (ratingB - ratingA) / DENOMINATOR))

  scoreCoefficient = 1
  if score == 0.5: scoreCoefficient = 0.5

  newRatingA = round(ratingA + K * scoreCoefficient * (score - expectedA))

  return newRatingA

def finish_game(duelName):
    duel = duels.get(duelName)
    if not duel or duel.finished:
        return

    duel.finished = True
    
    p1 = duel.player1
    p2 = duel.player2
    
    p1_result = 0.5
    if p1.total_score > p2.total_score:
        p1_result = 1.0
    elif p1.total_score < p2.total_score:
        p1_result = 0.0
        
    p2_result = 1.0 - p1_result
    
    new_r1 = calculateRatings(p1.userObj.rating, p2.userObj.rating, p1_result)
    new_r2 = calculateRatings(p2.userObj.rating, p1.userObj.rating, p2_result)
    
    updateUserRating(p1.username, new_r1)
    updateUserRating(p2.username, new_r2)
    
    socketio.emit(duelName, {
        "code": "end_game",
        "scores": {p1.username: p1.total_score, p2.username: p2.total_score},
        "ratings": {p1.username: new_r1, p2.username: new_r2}
    })
    
    del duels[duelName]

def start_new_round(duelName):
    duel = duels.get(duelName)
    if not duel: return

    duel.index += 1
    
    if duel.index >= 3:
        finish_game(duelName)
        return
        
    duration = 300
    if duel.tasks[duel.index].difficulty == "Простой": duration = 60
    elif duel.tasks[duel.index].difficulty == "Средний": duration = 90
    elif duel.tasks[duel.index].difficulty == "Сложный": duration = 120
    
    duel.roundDuration = duration
    duel.startRound()
    
    socketio.emit(duelName, {
        "code": "new_round", 
        "task": duel.tasks[duel.index].description, 
        "duration": duration
    })

def match_found(player1: User, player2: User):
    duelName = f"Duel_{secrets.token_urlsafe(16)}"
    duels[duelName] = Duel(duelName, player1, player2)
    
    socketio.emit(f"matchmaking_{player1.name}", {
        "code": "match_found", 
        "duelName": duelName, 
        "opponent": {"name": player2.name, "rating": player2.rating}
    })
    socketio.emit(f"matchmaking_{player2.name}", {
        "code": "match_found", 
        "duelName": duelName, 
        "opponent": {"name": player1.name, "rating": player1.rating}
    })
    
    socketio.on_event(duelName, lambda data: handle_duel(duelName, data))

def handle_duel(duelName, data):
    duel = duels.get(duelName)
    if not duel: return

    operation = data.get("operation")
    username = data.get("username")
    
    if operation == "answer":
        allowed_time = duel.roundDuration + 2
        elapsed = (datetime.now() - duel.roundStartTime).total_seconds()
        
        if elapsed > allowed_time:
            socketio.emit(duelName, {
                "code": "answerResponse",
                "score": 0,
                "toUser": username,
                "isCorrect": False,
                "message": "Time is up!"
            })
            duel.getPlayer(username).scores[duel.index] = 0
        else:
            correct_answer = duel.tasks[duel.index].answer
            user_answer = data.get("answer", "").strip()
            
            is_correct = (user_answer.lower() == correct_answer.lower())
            score = duel.calculateScore(username, is_correct)
            
            socketio.emit(duelName, {
                "code": "answerResponse",
                "score": score,
                "toUser": username,
                "isCorrect": is_correct,
                "correctAnswer": correct_answer
            })
        if (duel.player1.scores[duel.index] is not None and 
            duel.player2.scores[duel.index] is not None):
            
            socketio.sleep(3)
            start_new_round(duelName)
        
    elif operation == "join":
        player = duel.getPlayer(username)
        player.ready = True
        if duel.player1.ready and duel.player2.ready:
            start_new_round(duelName)



@socketio.on("leave_queue")
def leave_queue(username):
  for userInQueue in userQueue:
    if userInQueue.userObj.name == username:
        userQueue.remove(userInQueue)
        print(userQueue)
        return
    
@socketio.on("matchmaking")
def handle_matchmaking(username):
    user = getUser(username)
    if not user: return
    global userQueue
    userQueue = [u for u in userQueue if u.userObj.name != username]

    found_opponent = None
    for item in userQueue:
        if abs(item.userObj.rating - user.rating) <= 200:
            found_opponent = item
            break
    
    if found_opponent:
        userQueue.remove(found_opponent)
        match_found(found_opponent.userObj, user)
    else:
        userQueue.append(UserInQueue(user))