##   --Rishi--
## To make calculations for the stages information
import datetime as datetime

from app.models import User, Stage, Shot
from app.timeConvert import utc_to_nsw, nsw_to_utc
from datetime import datetime
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

def avg_and_stdev(stageIDs):
    scores = []
    for id in stageIDs:
        shots = Shot.query.filter_by(stageID=id).all()
        for shot in shots:
            pass
    average = 0
    stDev = 0
    return

def stats_of_period(userID, periodType, start, end):
    """
    Function which checks the periodType string
    :param userID: The shooter whose stage stats are to be viewed
    :param periodType: The time period interval
    :param start: The start of measurement
    :param end: The end of measurement
    :return:
    """
    dayStartAEST = utc_to_nsw(start).replace(hour=0, minute=0, second=0, microsecond=0)
    dayEndAEST = utc_to_nsw(end).replace(hour=23, minute=59, second=59, microsecond=0)
    start = nsw_to_utc(dayStartAEST)
    end = nsw_to_utc(dayEndAEST)
    stages = Stage.query.filter(Stage.timestamp.between(start, end), Stage.userID == userID).all()

    if periodType == "day":
        return stats_day(stages)
    if periodType == "week":
        return stats_week(stages)
    if periodType == "month":
        return stats_month(stages)
    if periodType == "year":
        return stats_year(stages)

def stats_day(stages):
    """
    Finds the average and standard deviation for shots based off day
    :param stages: List of stagess
    :return: Statistics in the form [{'avg': 48.5, 'stDev': 0.35, 'date': datetime.datetime(2021, 3, 27, 3, 5, 54)}, ....]
    """
    stats = []
    stagesList = []
    date = 0

    for stage in stages:
        time = (stage.timestamp).replace(hour=0, minute=0, second=0)
        if time == date:
            stagesList.append(stage)
            stats.pop(-1)
        else:
            date = time
            stagesList = [stage]

        data = conversion(stagesList)
        avg_stdv = {}
        avgScore = sum(data[1])/len(data[1])
        avgStdev = sum(data[3])/len(data[3])
        avg_stdv["avg"] = avgScore
        avg_stdv["stDev"] = avgStdev
        avg_stdv["date"] = date
        stats.append(avg_stdv)

    return stats

def stats_week(stages):
    return
def stats_month(stages):
    return

def stats_year(stages):
    stats = []
    stagesList = []
    date = []
    stages.sort(key=lambda x: x.timestamp, reverse=False)

    for stage in stages:
        time = (stage.timestamp)
        if time.year == date:
            stagesList.append(stage)
            stats.pop(-1)
        else:
            date = time.year
            stagesList = [stage]

        data = conversion(stagesList)
        avg_stdv = {}
        avgScore = sum(data[1]) / len(data[1])
        avgStdev = sum(data[3]) / len(data[3])
        avg_stdv["avg"] = avgScore
        avg_stdv["stDev"] = avgStdev
        stats.append(avg_stdv)

    return stats



