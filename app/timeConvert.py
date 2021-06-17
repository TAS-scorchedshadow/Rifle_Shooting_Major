import pytz

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