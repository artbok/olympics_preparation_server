from peewee import *
from models.user import User
import bcrypt


def hash_password(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, stored_hash: str):
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


def createUser(username, password, rightsLevel):
    if getUser(username):
        return "user_already_exists"
    hashed_password = hash_password(password)
    User.create(name = username, password = hashed_password, rightsLevel = rightsLevel)
    return "ok"


def getUser(username) -> User:
    return User.get_or_none(User.name == username)


def isAdmin(username, password) -> str: #!!!!
    user: User = getUser(username)
    if not user or not verify_password(password, user.password):
        return 'wrong_credentials'
    if user.rightsLevel < 2:
        return 'access_denied'
    return 'ok'


def isUser(username, password) -> bool:
    user: User = getUser(username)
    if user and verify_password(password, user.password):
        return "ok"
    return "wrong_credentials"


def getUsers() -> list[User]:
    users = []
    for user in User.select().where(User.rightsLevel == 1):
        users.append(user.name)
    return users

def updateRating(name, deltaRating):
    user: User = getUser(name)
    user.rating += deltaRating
    
    ratingChangesList = list(map(int, user.ratingChanges.split('/')))
    ratingChangesList.append(deltaRating)
    user.ratingChanges = '/'.join(map(str, ratingChangesList))
    user.save()
    return user.ratingChanges

def getProfile(name):
    user: User = getUser(name)
    if not user:
        return None
    
    return {
        "rating": user.rating,
        "username": user.name,
        "rightsLevel": user.rightsLevel,
        "totalTime": user.totalTime,
        "solvedCorrectly": user.solvedCorrectly,
        "solvedIncorrectly": user.solvedIncorrectly,
        "ratingChanges": list(map(int, user.ratingChanges.split('/')))
    }

if not User.table_exists():
    User.create_table()
    print("Table 'User' created")