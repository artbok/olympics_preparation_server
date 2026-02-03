from peewee import *
from models.user import User
from json import *

def createUser(name, password, rightsLevel):
    User.create(name = name, password = password, rightsLevel = rightsLevel)


def getUser(name) -> User:
    return User.get_or_none(User.name == name)


def isAdmin(name, password) -> str:
    user: User = getUser(name)
    if not user or user.password != password:
        return 'authError'
    if user.rightsLevel < 2:
        return 'accessError'
    return 'ok'


def isUser(name, password) -> bool:
    user: User = getUser(name)
    if user and user.password == password:
        return True
    return False


def getUsers() -> list[User]:
    users = []
    for user in User.select().where(User.rightsLevel == 1):
        users.append(user.name)
    return users

def getRatingChanges(name):
    user: User = getUser(name)
    return map(int, user.ratingChanges.split('/'))

def addRatingChange(user, newDeltaRating):
    ratingChangesList = user.getRatingChanges()
    ratingChangesList.append(newDeltaRating)

    if len(ratingChangesList)>10:
        return '/'.join(ratingChangesList[-10:])
    return '/'.join(ratingChangesList)
    
def updateRating(name, deltaRating):
    user: User = getUser(name)
    user.rating += deltaRating
    User.addRatingChange(user,deltaRating)



if not User.table_exists():
    User.create_table()
    print("Table 'User' created")

