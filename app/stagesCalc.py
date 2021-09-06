## To make calculations for the stages information
import datetime as datetime
import json

from app.models import User, Stage, Shot
from app.timeConvert import utc_to_nsw, nsw_to_utc
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
    query = Stage.query.filter_by(userID=userID).order_by(Stage.timestamp).all()
    stages = []
    for j in query:
        if end > (j.timestamp) > start:
            stages.append(j)
    return conversion(stages)


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
        print(avg_stdv)
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

    print(stats)
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


day_start = datetime.strptime("1/1/2018", "%d/%m/%Y")
day_end = datetime.strptime("12/12/2018", "%d/%m/%Y")
stats_of_period(65, "day", day_start, day_end)


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
def HighestStage(userID):
    HighestStage = 0
    stages = Stage.query.filter_by(userID=userID).all()
    length = len(stages)
    for i in range(length):
        if stages[i] > stages[HighestStage]:
            HighestStage = stages[i]
    return HighestStage


# By Andrew Tam
def LowestStage(userID):
    LowestStage = 0
    stages = Stage.query.filter_by(userID=userID).all()
    length = len(stages)
    for i in range(length):
        if stages[i] < stages[LowestStage]:
            LowestStage = stages[i]
    return LowestStage


# Dylan Huynh & Henry Guo
def plotsheet_calc(stage, user):
    """
        Calculating data required for the display of plotsheet.html

        :parameter stage: Stage object
        :parameter user: User object

        :return: Landing html page
    """
    # Dylan
    shots = Shot.query.filter_by(stageID=stage.id).all()
    data = {}

    formattedList = []
    scoreList = []
    num = 1
    letter = ord("A")
    shotTotal = 0
    shotsList = [stat for stat in enumerate(shots)]
    shotDuration = 'N/A'
    # Shot duration is calculated by the time between registered shots on the target --> 1st shot has no duration.
    for idx, shot in shotsList:
        scoreList.append(shot.score)
        if idx != 0:
            start = shotsList[idx - 1][1].timestamp
            diff = (shot.timestamp - start).total_seconds()
            if int(diff / 60) == 0:
                shotDuration = "{}s".format(int(diff % 60))
            else:
                shotDuration = "{}m {}s".format(int(diff / 60), int(diff % 60))
        if shot.sighter:
            formattedList.append([chr(letter), shot.xPos, shot.yPos, str(shot.score), shotDuration, 0])
            letter += 1
        else:
            formattedList.append([str(num), shot.xPos, shot.yPos, str(shot.score), shotDuration, 0])
            num += 1
            shotTotal += shot.score
    jsonList = json.dumps(formattedList)
    data["jsonList"] = jsonList

    # Formatting calculated data for the particular stage.
    stageResponse = stage.stageStats()
    stageStats = [round(stat, 2) for stat in stageResponse]
    stageDuration = "{}m {}s".format(int(stageResponse[4] / 60), stageResponse[4] % 60)
    stageStats[4] = stageDuration
    data['stageStats'] = stageStats

    # Total appended to list to match the format of existing plot sheet
    formattedList.append(["Total", 0, 0, str(shotTotal), stageDuration])
    data['formattedList'] = formattedList

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

    dayStats = [0, 0, 0, 0, 0]
    for shoot in dayStages:
        if shoot.userID == stage.userID:
            count += 1
            dayResponse = shoot.stageStats()
            for i, stat in enumerate(dayResponse):
                dayStats[i] = dayStats[i] + stat
            dayX += shoot.groupX
            dayY += shoot.groupY
            myStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
        elif shoot.distance == stage.distance:
            otherStages.append({'groupX': shoot.groupX, 'groupY': shoot.groupY})
    dayAvg = [dayX / count, dayY / count]
    myStages = json.dumps(myStages)
    otherStages = json.dumps(otherStages)
    for i, stat in enumerate(dayStats):
        dayStats[i] = round(stat / count, 2)
    dayDuration = "{}m {}s".format(int(dayStats[4] / 60), int(dayStats[4] % 60))
    dayStats[4] = dayDuration
    data['dayStats'] = dayStats
    data['dayAvg'] = dayAvg
    data['myStages'] = myStages
    data['otherStages'] = otherStages

    # Get Season Stats
    seasonResponse = user.seasonStats()
    seasonStats = [round(stat, 2) for stat in seasonResponse]
    seasonDuration = "{}m {}s".format(int(seasonResponse[4] / 60), seasonResponse[4] % 60)
    seasonStats[4] = seasonDuration
    data['seasonStats'] = seasonStats

    data['range'] = json.dumps(stage.distance)

    return data
