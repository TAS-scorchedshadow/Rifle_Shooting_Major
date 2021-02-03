import numpy
from datetime import datetime


def validateShots(data):
    """
    :param data: TO BE FILLED
    :return: Information of the shoot session
    """
    totalShots = 0      # Total number of shots
    countingShots = 0   # Total, excluding sighters
    newShoot = {'id': 0, 'username': "", 'time': 0, 'duration': 0, 'validShots': [],
                'groupSize': 0.0, 'groupCentreX': 0.0, 'groupCentreY': 0.0}
    validShotList = []
    runningScore = {'score': 0, 'Vscore': 0}
    for individualShot in data['shots']:
        x = individualShot['valid']
        if x:
            score = getScore(individualShot)
            individualShot['ts'] = msToDatetime(individualShot['ts'])
            individualShot['score'] = score['score']
            individualShot['Vscore'] = score['Vscore']
            sighter = checkSighter(individualShot)
            individualShot['sighter'] = sighter
            validShotList.append(individualShot)
            totalShots += 1
            if not sighter:
                countingShots += 1
                runningScore['score'] += score['score']
                runningScore['Vscore'] += score['Vscore']
    # Check to see if number of validated shots met expected value
    if totalShots != data["n_shots"]:
        print("validateShots validated: ", str(totalShots), "shots. Which differed from the original JSON",
              str(data["n_shots"]))
    # Send all the relevant data to a new dictionary, newShoot
    newShoot['id'] = data['_id']
    newShoot['username'] = data['name']
    firstShotTime = validShotList[0]['ts']              # time of first shot
    newShoot['time'] = firstShotTime
    newShoot['dateTime'] = firstShotTime
    newShoot['groupSize'] = data['stats_group_size']
    newShoot['groupCentreX'] = data['stats_group_center']['x']
    newShoot['groupCentreY'] = data['stats_group_center']['y']
    newShoot['validShots'] = validShotList
    newShoot['totalShots'] = countingShots
    newShoot['totalScore'] = str(runningScore['score']) + "." + str(runningScore['Vscore'])
    newShoot['stats'] = shotStats(validShotList)
    newShoot['shotList'] = shootList(validShotList)
    return newShoot


# Gets shot statistics
def shotStats(shoot):
    """
    :param shoot: Data of the shoot session
    :return: Calculation of median, mean and standard deviation
    """
    stats = {}
    shots = []
    for i in shoot:
        if not i['sighter']:
            shots.append(i['score'])
    stats['median'] = numpy.median(shots)
    stats['mean'] = numpy.mean(shots)
    stats['std'] = numpy.std(shots)
    return stats


def msToDatetime(ms):
    """
    :param ms: Time in millisecond format?
    :return: Time in format of YYYY/MM/DD HH:MM:SS
    """
    date = datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return date


def strTimeDifference(str1,str2):
    """
    :param str1: Former time
    :param str2: Latter time
    :return: Time gap between former and latter times
    :rtype: string
    """
    time1 = datetime.strptime(str1,'%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(str2, '%Y-%m-%d %H:%M:%S')
    difference = time2 -time1
    return str(difference)


# Gets shot statistics
def shootList(shoot):
    """
    :param shoot: Dictionary of shot number and its value from a shoot session
    :return: List of individual shot scores
    """
    shots = []
    for i in shoot:
        shots.append(i['value'])
    return shots


# Reformats score into a dictionary of score and Vscore
def getScore(shot):
    """
    :param shot: Individual shot info
    :return: Score of the shot
    """
    score = {'score': 0, 'Vscore': 0}  # Vscore = 0 if none was given
    if shot['value'] == "V":                # JSON includes array if shot included a Vscore
        score['score'] = shot['score'][0]
        score['Vscore'] = shot['score'][1]
    else:
        score['score'] = shot['score']
    return score


# Checks if the shot is a sighter
def checkSighter(shot):
    """
    :param shot: Individual shot
    :return: Whether the sighter was used?
    """
    try:
        return shot['sighter']
    except KeyError:
        return False
