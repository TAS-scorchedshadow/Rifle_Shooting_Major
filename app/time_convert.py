import os

import pytz
from datetime import datetime

from app import app
from datetime import timezone


@app.template_filter('utc_to_nsw')
def utc_to_nsw(utc_dt):
    """
    Converts database time(naive utc) to NSW time
    Does not work with datetime.date objects

    :param utc_dt: A datetime object in UTC
    :return: A datetime object in NSW Australia time
    """
    nsw = pytz.timezone('Australia/NSW')
    return utc_dt.astimezone(tz=nsw)


def get_season_times():
    begin = datetime.strptime(os.environ["SEASON_START"], '%d/%m/%Y')
    end = datetime.strptime(os.environ["SEASON_END"], '%d/%m/%Y')
    return begin, end


def nsw_to_utc(nsw_dt):
    """
    Converts NSW time to database time(naive utc)

    :param nsw_dt: Aware datetime object(tz=NSW)
    :return: Aware datetime object(tz=utc)
    """
    return nsw_dt.astimezone(pytz.utc)


def get_school_year(gradYr):
    """
    Determines the user's school year based on their graduation year & the current time

    :return: school_year as integer ie. 7,8,9,10,11,12
    """
    try:
        curYear = datetime.today().year
        schoolYear = curYear - int(gradYr) + 12
        return schoolYear
    except:
        print("Students graduation year is not defined")


def get_grad_year(schoolYr):
    curYear = datetime.today().year
    gradYr = curYear - int(schoolYr) + 12
    return gradYr


def formatDuration(diff):
    if int(diff / 60) == 0:
        duration = "{}s".format(int(diff % 60))
    else:
        duration = "{}m {}s".format(int(diff / 60), int(diff % 60))
    return duration