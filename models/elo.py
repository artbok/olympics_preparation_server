from peewee import *
from models.user import User
from services.user_service import *

def calculateRatings(ratingA, ratingB, scoreA, scoreB):
  DENOMINATOR = 400
  K = 32

  expectedA = 1 / (1 + pow(10, (ratingB - ratingA) / DENOMINATOR))
  expectedB = 1 / (1 + pow(10, (ratingA - ratingB) / DENOMINATOR))

  scoreCoefficient = 1
  if scoreA == 0.5: scoreCoefficient = 0.5

  newRatingA = round(ratingA + K * scoreCoefficient * (scoreA - expectedA))
  newRatingB = round(ratingB + K * scoreCoefficient * (scoreB - expectedB))

  return [newRatingA, newRatingB]

def changeRating(nameA, nameB, ratingA, ratingB, scoreA, scoreB):
  newRatingA, newRatingB = calculateRatings(ratingA, ratingB, scoreA, scoreB)
  userA: User = getUser(nameA)
  userB: User = getUser(nameB)
  deltaRatingA=newRatingA-userA.rating
  deltaRatingB=newRatingB-userB.rating
  UpdateRating(nameA, deltaRatingA)
  UpdateRating(nameB, deltaRatingB)