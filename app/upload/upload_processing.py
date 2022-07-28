import numpy
from datetime import datetime


def validate_shots(data):
    """
    Takes in data from a shoot string, extracts the relevant info, changing data type if necessary.
    Returns a dictionary of the new shoot data.

    newShoot is stored in the following format:

    +------------------+------------+----------------------------------------------------------------------------------+
    | Variable Name    | Type       | Description                                                                      |
    +==================+============+==================================================================================+
    | ``id``           | int        | The unique identifier for the stage.                                             |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``username``     | str        | The username of the user who performed the shoot.                                |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``time``         | datetime   | The time the stage began.                                                        |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``distance``     | str        | The range the stage was performed at. Units are stored within the string.        |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``groupSize``    | float      | Size of the system calculated group ring.                                        |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``groupCentreX`` | float      | Centre of the group in the x (horizontal) plane.                                 |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``groupCentreY`` | float      | Centre of the group in the y (vertical) plane.                                   |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``validShots``   | list[dict] | List of all shots that the system deemed valid in the stage.                     |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``totalShots``   | int        | Total number of counting shots.                                                  |
    |                  |            | *Currently depreciated.*                                                         |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``totalScore``   | str        | Total score in "[score].[centres]" format.                                       |
    |                  |            | *Currently depreciated.*                                                         |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``stats``        | dict       | Stores a dictionary of median, mean, and standard deviation.                     |
    |                  |            | *Currently depreciated.*                                                         |
    +------------------+------------+----------------------------------------------------------------------------------+
    | ``shotList``     | list[str]  | Stores a list of shot string values (i.e. stored as HIT 2 3 4 5 V X)             |
    |                  |            | *Only used in upload_verify.html*                                                |
    +------------------+------------+----------------------------------------------------------------------------------+

    :param data: Dictionary of a shoot string
    :type data: dict
    :return: newShoot
    """
    totalShots = 0      # Total number of shots
    countingShots = 0   # Total, excluding sighters
    newShoot = {'id': 0, 'username': "", 'time': 0, 'distance': "",
                'groupSize': 0.0, 'groupCentreX': 0.0, 'groupCentreY': 0.0,
                'validShots': [], 'totalShots': 0}
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


def shot_stats(shoot):
    """
    Takes a list of valid shots and returns the median, mean, and STD of the shots.

    :param shoot: List of valid shots
    :type shoot: list
    :return: Dictionary of median, mean and standard deviation
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
    Takes in a time in millisecond format, and converts it into datetime form.

    :param ms: Time in millisecond format
    :return: Time in format of YYYY/MM/DD HH:MM:SS
    """
    date = datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return date


def shoot_list(shoot):
    """
    Returns a list of the raw shot values in a stage

    :param shoot: List of valid shots
    :type shoot: list
    :return: List of shot scores as a string
    """
    shots = []
    for i in shoot:
        shots.append(i['value'])
    return shots


# Reformats score into a dictionary of score and Vscore
def get_score(shot):
    """
    Reformats a score into a dictionary of score and Vscore

    :param shot: Individual shot info
    :type shot: dict
    :return: int containing score of the shot
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
    Check whether the current shot was a sighter by returning the value if it exists

    :param shot: Individual shot
    :type shot: dict
    :return: bool containing if current shot was a sighter.
    """
    try:
        return shot['sighter']
    except KeyError:
        return False
