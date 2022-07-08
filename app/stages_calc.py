## To make calculations for the stages information
import datetime as datetime
import json

from app.models import User, Stage, Shot
from app.time_convert import nsw_to_utc, format_duration, utc_to_nsw
from datetime import datetime
import statistics


# Rishi Wig
def stage_by_date(userID, start, end):
    """
    Queries database and creates list between the start & end dates specified

    :param userID: The database ID of the profile being viewed
    :param start: The start date specified by the user
    :param end: The end date specified by the user
    :return: The stages list to conversion function to obtain data required
    """
    query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp, Stage.timestamp.between(start, end)).all()
    return conversion(query)


# Rishi Wig
def stage_by_n(userID, amount):
    """
    Queries database and creates a list of stages with N (amount) objects

    :param userID: The database ID of the profile being viewed
    :param amount: The N number of stages which is wished to be seen by the user
    :return:
    """
    stages = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).limit(amount).all()
    return conversion(stages)


# Rishi Wig
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
            total.append((((trueTotal / totalPotential) * 100) / 100) * 50)
            avgScores.append(round((float(trueTotal / shots) * 10)))
            stDev.append(round((statistics.pstdev(tempStdev)), 1))

    return timestamps, avgScores, total, stDev, scores


# Rishi Wig
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


# Rishi Wig
def stats_day(stages):
    """
    Finds the average and standard deviation for shots based off day
    :param stages: List of stages
    :return: Statistics in the form [{'avg': 48.5, 'stDev': 0.35, 'date': datetime.datetime(2021, 3, 27, 3, 5, 54)}, ....]
    """
    stats = []
    stagesList = []
    date = 0
    year = 0
    stages.sort(key=lambda x: x.timestamp, reverse=False)

    for stage in stages:
        time = (stage.timestamp).replace(hour=0, minute=0, second=0)
        if time == date and time.year == year:
            stagesList.append(stage)
            stats.pop(-1)
        else:
            date = time
            year = time.year
            stagesList = [stage]

        data = conversion(stagesList)
        avg_stdv = {}
        avgScore = sum(data[1]) / len(data[1])
        avgStdev = sum(data[3]) / len(data[3])
        avg_stdv["avg"] = avgScore
        avg_stdv["stDev"] = avgStdev
        avg_stdv["date"] = date
        stats.append(avg_stdv)

    return stats


# Rishi Wig
def stats_week(stages):
    stats = []
    stagesList = []
    date = 0
    years = 0
    stages.sort(key=lambda x: x.timestamp, reverse=False)
    for stage in stages:
        year = (stage.timestamp).year
        time = datetime.date(stage.timestamp).isocalendar()[1]
        if time == date and year == years:
            stagesList.append(stage)
            stats.pop(-1)
        else:
            date = time
            years = year
            stagesList = [stage]
        data = conversion(stagesList)
        avg_stdv = {}
        avgScore = sum(data[1]) / len(data[1])
        avgStdev = sum(data[3]) / len(data[3])
        avg_stdv["avg"] = avgScore
        avg_stdv["stDev"] = avgStdev
        avg_stdv["date"] = data[0][0]
        stats.append(avg_stdv)

    return stats


# Rishi Wig
def stats_month(stages):
    stats = []
    stagesList = []
    date = 0
    years = 0
    stages.sort(key=lambda x: x.timestamp, reverse=False)
    for stage in stages:
        time = (stage.timestamp)
        if time.month == date and time.year == years:
            stagesList.append(stage)
            stats.pop(-1)
        else:
            date = time.month
            stage = time.year
            stagesList = [stage]
        data = conversion(stagesList)
        avg_stdv = {}
        avgScore = sum(data[1]) / len(data[1])
        avgStdev = sum(data[3]) / len(data[3])
        avg_stdv["avg"] = avgScore
        avg_stdv["stDev"] = avgStdev
        avg_stdv["date"] = data[0]
        stats.append(avg_stdv)

    return stats


# Rishi Wig
def stats_year(stages):
    stats = []
    stagesList = []
    date = 0
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
        avg_stdv["date"] = data[0]
        stats.append(avg_stdv)

    return stats


# By Andrew Tam
def groupAvg(userID):
    XTotal = 0
    YTotal = 0
    stages = Stage.query.filter_by(userID=userID).all()
    length = len(stages)
    for i in range(length):
        XTotal = XTotal + stages[i].groupX
        YTotal = YTotal + stages[i].groupY
    groupXAvg = XTotal / length
    groupYAvg = YTotal / length

    return groupXAvg, groupYAvg


# By Andrew Tam
def highest_stage(userID, startDate, endDate, dist):
    stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.distance == dist,
                                Stage.userID == userID).all()
    highest = stages[0]
    for stage in stages:
        if stage.score_as_percent() > highest.score_as_percent():
            highest = stage
    return highest


# By Andrew Tam
def lowest_stage(userID, startDate, endDate, dist):
    stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.distance == dist,
                                Stage.userID == userID).all()
    lowest = stages[0]
    for stage in stages:
        if stage.score_as_percent() < lowest.score_as_percent():
            lowest = stage
    return lowest


# Dylan Huynh & Henry Guo
def plotsheet_calc(stage, user):
    """
        Calculating data required for the display of plotsheet.html

        :parameter stage: Stage object
        :parameter user: User object

        :return: Landing html page
    """
    # Dylan
    data = {}

    stage.init_shots()
    rtnData = stage.format_shots()
    allShots = rtnData["sighters"] + rtnData["scores"]
    data["jsonList"] = json.dumps(allShots)

    stage.init_stage_stats()
    data["formattedList"] = allShots + [{"displayChar": "Total",
                                         "scoreVal": f"{stage.total}.{stage.totalVScore}/{stage.totalPossible}",
                                         "shotDuration": format_duration(stage.duration)}]

    data['stageStats'] = {"mean": round(stage.mean, 2), "median": round(stage.median, 2), "std": round(stage.std, 2),
                          "groupSize": round(stage.groupSize, 2), "duration": format_duration(stage.duration)}

    # Henry

    # Calculating statistics for stages shot on the same day
    dayStages = stage.same_day()
    # dayX and dayY refers to the grouping coordinates
    dayX = 0
    dayY = 0
    count = 0
    # stages of other people's shoots on the same day and stores their grouping info
    otherStages = []
    # stages of the selected user's shoots on the same day and stores their grouping info
    myStages = []
    dayStats ={"mean": 0, "median": 0, "std": 0, "groupSize": 0, "duration": 0}
    for shoot in dayStages:
        if shoot.userID == stage.userID:
            count += 1
            stage.init_stage_stats()
            dayStats["mean"] += stage.mean
            dayStats["median"] += stage.median
            dayStats["std"] += stage.std
            dayStats["groupSize"] += stage.groupSize
            dayStats["duration"] += stage.duration

            dayX += shoot.groupX
            dayY += shoot.groupY
            myStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
        elif shoot.distance == stage.distance:
            otherStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
    myStages = json.dumps(myStages)
    otherStages = json.dumps(otherStages)
    for key in dayStats:
        dayStats[key] = round(dayStats[key] / count, 2)
    dayStats["duration"] = format_duration(dayStats["duration"])
    data['dayStats'] = dayStats
    data['myStages'] = myStages
    data['otherStages'] = otherStages

    # Get Season Stats
    seasonResp = user.season_stats(stage.distance)
    data['season_stats'] = {"mean": round(seasonResp["mean"], 2), "median": round(seasonResp["median"], 2),
                           "std": round(seasonResp["std"], 2), "groupSize": round(seasonResp["groupSize"], 2),
                           "duration": format_duration(seasonResp["duration"])}

    data['range'] = json.dumps(stage.distance)

    return data


def target_calc(stage):
    data = {}

    stage.init_shots()
    rtnData = stage.format_shots()
    allShots = rtnData["sighters"] + rtnData["scores"]
    data["jsonList"] = json.dumps(allShots)

    stage.init_stage_stats()
    data["formattedList"] = allShots + [{"displayChar": "Total",
                                         "scoreVal": f"{stage.total}.{stage.totalVScore}/{stage.totalPossible}",
                                         "shotDuration": format_duration(stage.duration)}]

    data['stageStats'] = {"mean": round(stage.mean, 2), "median": round(stage.median, 2), "std": round(stage.std, 2),
                          "groupSize": round(stage.groupSize, 2), "duration": format_duration(stage.duration)}
    data['range'] = json.dumps(stage.distance)
    return data


def total_shots_taken(stages):
    total = 0
    for stage in stages:
        stage.init_shots()
        total += len(stage.shotList)
    return total


def days_present(stages):
    """
    Retains a list of times that needs 

    :param stages:
    :return: List of datetime objects
    """
    return