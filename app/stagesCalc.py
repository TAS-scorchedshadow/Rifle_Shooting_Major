## To make calculations
from app.models import User, Stage, Shot


def stage_by_date(userID, start, end):
    query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).all()
    stages = []
    for j in query:
        if end > (j.timestamp) > start:
            stages.append(j)
    return conversion(stages)

def stage_by_n(userID, amount):
    query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).limit(amount).all()
    return conversion(query)


def conversion(stages_array):
    timestamps = []
    stageIDs = []
    for j in stages_array:
        timestamps.append(j.timestamp)
        stageIDs.append(j.id)
    avgScores = []
    for c in stageIDs:
        query = Shot.query.filter_by(stageID=c).all()
        total = 0
        shots = 0
        for objects in query:
            if objects.sighter == True:
                total += objects.score
                shots += 1
        avgScores.append(float(total / shots))
    return timestamps, avgScores