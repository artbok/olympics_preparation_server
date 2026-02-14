from peewee import *
from models.duel import Duel

def createDuel(username1, username2, score1, 
               score2, newRating1, newRating2):
    Duel.create(username1 = username1, username2 = username2, 
                score1 = score1, score2 = score2, 
                newRating1 = newRating1, 
                newRating2 = newRating2)

def getDuels(username):
    if username == None:
        return Duel.select().dicts()
    return Duel.select().where((Duel.username1 == username) | (Duel.username2 == username)).dicts()


if not Duel.table_exists():
    Duel.create_table()
    print("Table 'Duel' created")