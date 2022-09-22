from datetime import datetime

from flask import Blueprint

shell_bp = Blueprint('shell_bp', __name__)


def clear_table(db, table):
    items = table.query.all();
    for i in items:
        db.session.delete(i)
    db.session.commit()
    return


def new_club(db, Club, club_name: str) -> object:
    """
    Generates a new club from terminal. Season dates are set to the beginning of the current year
    :param db: app db object
    :param Club: club model
    :param club_name: name of club
    :return: new club object
    """
    start = datetime(datetime.today().year, 1, 1)
    end = datetime(datetime.today().year, 12, 31)
    club = Club(name=club_name, email_setting=0, season_start=start, season_end=end)
    db.session.add(club)
    db.session.commit()
    return club
