def calculateRatings(ratingA, ratingB, scoreA, scoreB):
  DENOMINATOR = 400
  K = 32

  expectedA = 1 / (1 + pow(10, (ratingB - ratingA) / DENOMINATOR))
  expectedB = 1 / (1 + pow(10, (ratingA - ratingB) / DENOMINATOR))

  scoreCoefficient = 1
  if scoreA == 0.5: scoreCoefficient = 0.5

  newRatingA = round(ratingA + K * scoreCoefficient * (scoreA - expectedA))
  newRatingB = round(ratingB + K * scoreCoefficient * (scoreB - expectedB))

  return {"ratingA": newRatingA, "ratingB": newRatingB}

print(calculateRatings(2700, 2800, 0, 1))
print(calculateRatings(300, 3000, 1, 0 ))