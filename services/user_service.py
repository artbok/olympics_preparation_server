from peewee import *
from models.user import User


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


if not User.table_exists():
    User.create_table()
    print("Table 'User' created")
