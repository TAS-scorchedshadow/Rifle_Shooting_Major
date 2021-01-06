import numpy
from datetime import datetime


def validateShots(data):
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
    lastShotTime = validShotList[totalShots - 1]['ts']  # time of last shot
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
    date = datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return date


def strTimeDifference(str1,str2):
    time1 = datetime.strptime(str1,'%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(str2, '%Y-%m-%d %H:%M:%S')
    difference = time2 -time1
    return str(difference)


# Gets shot statistics
def shootList(shoot):
    shots = []
    for i in shoot:
        shots.append(i['value'])
    return shots


# Reformats score into a dictionary of score and Vscore
def getScore(shot):
    score = {'score': 0, 'Vscore': 0}  # Vscore = 0 if none was given
    if shot['value'] == "V":                # JSON includes array if shot included a Vscore
        score['score'] = shot['score'][0]
        score['Vscore'] = shot['score'][1]
    else:
        score['score'] = shot['score']
    return score


# Checks if the shot is a sighter
def checkSighter(shot):
    try:
        return shot['sighter']
    except KeyError:
        return False
