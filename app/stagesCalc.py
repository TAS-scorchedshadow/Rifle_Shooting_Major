##   --Rishi--
## To make calculations for the stages information

from app.models import User, Stage, Shot
import statistics

def stage_by_date(userID, start, end):
    """
    Queries database and creates list between the start & end dates specified

    :param userID: The database ID of the profile being viewed
    :param start: The start date specified by the user
    :param end: The end date specified by the user
    :return: The stages list to conversion function to obtain data required
    """
    query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).all()
    stages = []
    for j in query:
        if end > (j.timestamp) > start:
            stages.append(j)
    return conversion(stages)

def stage_by_n(userID, amount):
    """
    Queries database and creates a list of stages with N (amount) objects

    :param userID: The database ID of the profile being viewed
    :param amount: The N number of stages which is wished to be seen by the user
    :return:
    """
    stages = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).limit(amount).all()
    return conversion(stages)


def conversion(stages_array):
    """
    Obtains the list of stage objects to create lists of data required

    :param stages_array: The list of stage objects specified
    :return timestamps: List of the datetimes of the stages
    :return avgScores: List of the average score from the stages
    :return total: List of the total score from the stages, out of 50 (created through percentages)
    :return stDev: List of the standard deviations from the stages
    :return scores: List of list of all of the scores in the stage, with V replacing scores of 5 (convention)
    """
    timestamps = []
    stageIDs = []
    for j in stages_array:
        timestamps.append(j.timestamp)
        stageIDs.append(j.id)

    scores = []
    avgScores = []
    total = []
    stDev = []

    for c in stageIDs:
        query = Shot.query.filter_by(stageID=c).all()
        trueTotal = 0
        shots = 0
        tempStdev = []
        tempScore = []
        for objects in query:
            if not objects.sighter:
                trueTotal += objects.score
                shots += 1
                tempStdev.append(objects.score)
                if objects.vScore == 1:
                    tempScore.append("V")
                else:
                    tempScore.append(objects.score)
        scores.append(tempScore)
        totalPotential = 5 * shots

        if shots != 0 and totalPotential != 0:
            total.append((((trueTotal/totalPotential)*100)/100)*50)
            avgScores.append(round((float(trueTotal / shots)*10)))
            stDev.append(round((statistics.pstdev(tempStdev)),1))

    return timestamps, avgScores, total, stDev, scores

