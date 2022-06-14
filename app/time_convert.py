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


def nsw_to_utc(nsw_dt):
    """
    Converts NSW time to database time(naive utc)

    :param nsw_dt: Aware datetime object(tz=NSW)
    :return: Aware datetime object(tz=utc)
    """
    return nsw_dt.astimezone(pytz.utc)


def get_season_times():
    try:
        begin = datetime.strptime(os.environ["SEASON_START"], '%d/%m/%Y')
        end = datetime.strptime(os.environ["SEASON_END"], '%d/%m/%Y')
    except ValueError:
        # Setting defaults to the beginning and end of the year
        currYr = datetime.today().year
        begin = datetime(currYr, 1, 1)
        end = datetime(currYr, 12, 31)
    return begin, end


def get_grad_year(schoolYr):
    currYr = datetime.today().year
    try:
        gradYr = currYr - int(schoolYr) + 12
    except ValueError:
        gradYr = "None"
    return gradYr


def format_duration(secs_diff):
    if int(secs_diff / 60) == 0:
        duration = "{}s".format(int(secs_diff % 60))
    else:
        duration = "{}m {}s".format(int(secs_diff / 60), int(secs_diff % 60))
    return duration
