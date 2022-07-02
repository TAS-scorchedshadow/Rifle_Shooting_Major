import numpy
from datetime import datetime


def validate_shots(data):
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
            score = get_score(individualShot)
            individualShot['ts'] = ms_to_datetime(individualShot['ts'])
            individualShot['score'] = score['score']
            individualShot['Vscore'] = score['Vscore']
            sighter = check_sighter(individualShot)

            individualShot['sighter'] = sighter
            validShotList.append(individualShot)
            totalShots += 1
            if not sighter:
                countingShots += 1
                runningScore['score'] += score['score']
                runningScore['Vscore'] += score['Vscore']
    # Check to see if number of validated shots met expected value
    if totalShots != data["n_shots"]:
        print("validate_shots validated: ", str(totalShots), "shots. Which differed from the original JSON",
              str(data["n_shots"]))
    # Send all the relevant data to a new dictionary, newShoot
    newShoot['id'] = data['_id']
    newShoot['username'] = data['name']
    firstShotTime = validShotList[0]['ts']
    newShoot['time'] = firstShotTime
    newShoot['distance'] = data['distance']
    # if issue_code == 2:
    #     data['stats_group_size'] = 0
    #     data['stats_group_center']['x'], data['stats_group_center']['y'] = getGroupSize(validShotList)
    newShoot['groupSize'] = data['stats_group_size']
    newShoot['groupX'] = data['stats_group_center']['x']
    newShoot['groupY'] = data['stats_group_center']['y']
    newShoot['validShots'] = validShotList
    newShoot['totalShots'] = countingShots
    newShoot['totalScore'] = str(runningScore['score']) + "." + str(runningScore['Vscore'])
    newShoot['stats'] = shot_stats(validShotList)
    newShoot['shotList'] = shoot_list(validShotList)
    return newShoot


# Gets shot statistics
def shot_stats(shoot):
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


def ms_to_datetime(ms):
    """
    :param ms: Time in millisecond format?
    :return: Time in format of YYYY/MM/DD HH:MM:SS
    """
    date = datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return date


# Gets shot statistics
def shoot_list(shoot):
    """
    :param shoot: Dictionary of shot number and its value from a shoot session
    :return: List of individual shot scores
    """
    shots = []
    for i in shoot:
        shots.append(i['value'])
    return shots


# Reformats score into a dictionary of score and Vscore
def get_score(shot):
    """
    :param shot: Individual shot info
    :return: Score of the shot
    """
    # Note that for a HIT, shot[score] is 1, but shot[value] is HIT.
    score = {'score': 0, 'Vscore': 0}  # Vscore = 0 if none was given
    if shot['value'] == "V" or shot['value'] == "X":                # JSON includes array if shot included a Vscore
        score['score'] = 5                                          # todo: Need better handling for X
        score['Vscore'] = shot['score'][1]
    else:
        score['score'] = shot['score']
    return score


# Checks if the shot is a sighter
def check_sighter(shot):
    """
    :param shot: Individual shot
    :return: Whether the sighter was used?
    """
    try:
        return shot['sighter']
    except KeyError:
        return False
