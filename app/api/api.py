import json
import datetime as datetime

from flask import Blueprint, request, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import desc

from app import db
from app.models import User, Stage, Club
from app.stages_calc import stats_of_period, highest_stage, lowest_stage
from app.time_convert import get_grad_year, utc_to_nsw, format_duration, nsw_to_utc
from app.decorators import authorise_role
from tests.helper_functions.generate_data import generate_rand_stage

api_bp = Blueprint('api', __name__)


@api_bp.route('/submit_notes', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def submit_notes():
    """
    AJAX route for updating the notes of a stage from the plotsheet.

    :return: indication of submission success
    """
    # Function submits changes in notes
    data = request.get_data()
    loaded_data = json.loads(data)
    stage = Stage.query.filter_by(id=loaded_data[0]).first()
    stage.notes = loaded_data[1]
    db.session.commit()
    return jsonify({'success': 'success'})


@api_bp.route('/get_avg_shot_graph_data', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def get_avg_shot_data():
    """
    Collect shots for use in the averages line graph
    """
    end_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

    start_date = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d')
    start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())

    user_id = request.get_data().decode("utf-8")
    stats = stats_of_period(user_id, 'week', start_date, end_date)
    avg_scores = []
    st_dev = []
    timestamps = []
    for stage in stats:
        avg_scores.append(stage['avg'])
        st_dev.append(stage['stDev'])
        timestamps.append(stage['date'])
    formatted_time = []
    for date in timestamps:
        print(date)
        formatted_time.append(utc_to_nsw(date).strftime("%d/%m/%y"))
    graph_data = jsonify({'scores': avg_scores,
                          'times': formatted_time,
                          'sd': st_dev,
                          })
    return graph_data


@api_bp.route('/testdelshoot', methods=['GET', 'POST'])
@login_required
@authorise_role("DEV")
def testdelshoot():
    """
    Code that deletes all shoots put under the sbhs.admin user.
    """
    user = User.query.filter_by(username="sbhs.admin").first()
    stage_list = [stage for stage in Stage.query.filter_by(userID=user.id).all()]
    for stage in stage_list:
        print(stage)
        db.session.delete(stage)
    db.session.commit()
    return "OK"


def get_users(clubID=None):
    """
    If a club ID is provided, results will only include users from the club.

    :return: List of Dictionaries, Key: Username, Value: Username, first name, last name
    """
    club = Club.query.filter_by(id=clubID).first()
    if club:
        users = User.query.filter_by(clubID=clubID).all()
    else:
        users = User.query.all()
    return users


@api_bp.route('/get_names', methods=['GET'])
@login_required
@authorise_role("STUDENT")
def get_names():
    """
        Generates a list of names used to complete the autofill fields. Used in autofill.js.
        If a club ID is provided, results will only include users from the club.

        :return: List of Dictionaries, Key: Username, Value: Username, first name, last name
    """
    dev_access = 3
    # Verify club ID is valid
    if current_user.access == dev_access:
        users = get_users()
    else:
        user = User.query.filter_by(id=current_user.id).first()
        users = get_users(user.clubID)
    out = [{'label': "{} ({} {})".format(user.username, user.fName, user.sName), 'value': user.username} for user in
           users]
    return jsonify(out)


@api_bp.route('/get_shots', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def get_shots():
    """
    Collect shots for use in the recent shots card
    """

    data = request.get_data()
    loadedData = json.loads(data)
    userID = loadedData[0]
    # numLoaded are the number of tables already loaded
    numLoaded = loadedData[1]

    # Add up to 10 more tables
    totaltoLoad = numLoaded + 10

    # convert dateRange string into datetime objects
    dateRange = loadedData[2]
    if dateRange:
        dates = dateRange.split(' - ')
        # print(dates)
        startDate = datetime.datetime.strptime(dates[0], '%B %d, %Y')
        endDate = datetime.datetime.strptime(dates[1], '%B %d, %Y')
        # print(startDate, endDate)
        stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.userID == userID).order_by(
            desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    else:
        stages = Stage.query.filter_by(userID=userID).order_by(desc(Stage.timestamp)).all()[numLoaded: totaltoLoad]
    stagesList = []
    for stage in stages:
        data = stage.format_shots()
        stage.init_stage_stats()
        displayScore = f"{data['total']}/{data['totalPossible']}"
        stagesList.append({'scores': data["scores"],
                           'totalScore': displayScore,
                           'groupSize': round(stage.groupSize, 1),
                           'distance': stage.distance,
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': round(stage.std, 2),
                           'duration': format_duration(stage.duration),
                           'stageID': stage.id,
                           'sighters': data['sighters']
                           })
    return jsonify(stagesList)


@api_bp.route('/get_target_stats', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def get_target_stats():
    """
    Function provides databse information for ajax request in ajax_target.js
    """
    stageID = request.get_data().decode("utf-8")
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:  # Handles if stageID parameter is given but is not found in database
        return jsonify({'success': 'success'})
    return jsonify({'error': 'userID'})


@api_bp.route('/get_all_shots_season', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def get_all_shots_season():
    """
    Function collects every shot in the time-frame selected by the user
    """
    input_ = request.get_data().decode('utf-8')
    loadedInput = json.loads(input_)

    dist = loadedInput['distance']
    userID = loadedInput['userID']
    dateRange = loadedInput['dateRange']
    dates = dateRange.split(' - ')

    startDate = nsw_to_utc(datetime.datetime.strptime(dates[0], '%B %d, %Y'))
    endDate = nsw_to_utc(datetime.datetime.strptime(dates[1], '%B %d, %Y'))

    data = {'target': [], 'boxPlot': [], 'bestStage': [], 'worstStage': []}
    stages = Stage.query.filter(Stage.timestamp.between(startDate, endDate), Stage.distance == dist,
                                Stage.userID == userID).all()
    for stage in stages:
        stage.init_stage_stats()
        totalScore = stage.total
        fiftyScore = stage.score_as_percent()
        data['boxPlot'].append(fiftyScore)
        data['target'] = data['target'] + stage.format_shots()["scores"] + stage.format_shots()["sighters"]

    # Sort the scores for boxPlot so the lowest value can be taken.
    # The lowest value is used to determine the lower bound of the box plot
    data['boxPlot'].sort()
    if len(stages) > 0:
        # Get highest and lowest scoring stages
        highestStage = highest_stage(userID, startDate, endDate, dist)
        data['bestStage'] = {
            'id': highestStage.id,
            'score': round(highestStage.score_as_percent()),
            'time': str(utc_to_nsw(highestStage.timestamp))
        }
        lowestStage = lowest_stage(userID, startDate, endDate, dist)
        data['worstStage'] = {
            'id': lowestStage.id,
            'score': round(lowestStage.score_as_percent()),
            'time': str(utc_to_nsw(lowestStage.timestamp))
        }
    data = jsonify(data)
    return data


@api_bp.route('/submit_table', methods=['POST'])
@login_required
@authorise_role("STUDENT")
def submit_table():
    """
       Updates a user object (given by ID) with the new information provided in the table. Students can
       only change their own tables. Meanwhile, all other level users can only edit tables from their own club.
    """
    data = request.get_data().decode("utf-8")
    data = json.loads(data)
    userID = data[0]
    current_user_obj = User.query.filter_by(id=current_user.id).first()
    user = User.query.filter_by(id=userID).first()
    if userID != current_user.id:
        if current_user_obj.access < 1 or current_user_obj.clubID != user.clubID:
            return abort(403)
    tableDict = data[1]

    # In this case setattr changes the value of a certain field in the database to the given value.
    # e.g. user.sightHole = "5"
    if user:
        for field in tableDict:
            # Convert school year into graduation year
            if field == 'gradYr' and tableDict[field] is not None:
                try:
                    value = str(get_grad_year(tableDict[field]))
                except:
                    value = "None"
            else:
                value = tableDict[field]
            # email cannot be changed in order to prevent coaches from changing the emails on other accounts
            if value != "None" and field != 'email':
                setattr(user, field, value)
        db.session.commit()

    return jsonify({'success': 'success'})


@api_bp.route('/api/attendance', methods=["GET"])
@login_required
@authorise_role("STUDENT")
def api_attendace():
    users = api_num_shots_season_all();


@api_bp.route('/api/num_shots_season_all', methods=["GET"])
@login_required
@authorise_role("DEV")
def api_num_shots_season_all():
    users = User.query.all()
    user_list = []
    settings = Club.query.filter_by(id=0).first()
    for user in users:
        data = num_shots(user.id, settings.season_start, settings.season_end)
        user_list.append({"userID": user.id, "name": f"{user.fName} {user.sName}", "data": data})
    return {"users": user_list}


@api_bp.route('/api/num_shots_season', methods=["GET"])
@login_required
@authorise_role("STUDENT")
def api_num_shots_season():
    userID = request.args.get('userID')
    userObj = User.query.filter_by(id=userID)
    if userObj is None:
        abort(400)
    settings = Club.query.filter_by(id=userObj.clubID).first()

    return num_shots(userID, settings.season_start, settings.season_end)


def num_shots(userID, start, end):
    num = 0
    num_sessions = 0
    stages = Stage.query.filter(Stage.timestamp.between(start, end),
                                Stage.userID == userID).all()
    stages.sort(key=lambda x: x.timestamp)
    length = len(stages)
    if length != 0:
        num_sessions = 1
    for i, stage in enumerate(stages):
        if i < length - 1:
            if stages[i + 1].timestamp - stages[i].timestamp > datetime.timedelta(hours=12):
                num_sessions += 1
        # Initialise all shots
        stage.init_shots()
        num += len(stage.shotList)

    if num_sessions != 0:
        shots_per_session = round(num / num_sessions, 2)
    else:
        shots_per_session = 0
    return {"start_time": start.strftime("%d/%m/%Y"),
            "end_time": end.strftime("%d/%m/%Y"),
            "num_sessions": num_sessions, "num_stages": len(stages), "num_shots": num,
            "num_shots_per_session": shots_per_session}


def get_stages(userID: int, startDate: datetime, page: int) -> (list[dict], bool):
    """
    Paginates stages (6 stages per page). More recent stages will appear first. On the last stage
    returns true on the second parameter. If userID does not refer to a valid user no stages will be returned

    :param userID: int
    :param startDate: datetime object
    :param page: int
    :return: list[stage dict], final_page
    """
    items_per_page = 6
    final_page = False
    start_idx = (page - 1) * items_per_page
    end_idx = page * items_per_page
    if startDate:
        # Note filters out shots on the same day for some reason
        stages = Stage.query.filter(Stage.timestamp <= startDate + datetime.timedelta(days=1),
                                    Stage.userID == userID).order_by(
            desc(Stage.timestamp)).all()
    else:
        stages = Stage.query.filter_by(userID=userID).order_by(desc(Stage.timestamp)).all()
    if end_idx >= len(stages):
        final_page = True
    stages = stages[start_idx: end_idx]
    stagesList = []
    for stage in stages:
        data = stage.format_shots()
        stage.init_stage_stats()
        displayScore = f"{data['total']}/{data['totalPossible']}"
        stagesList.append({'scores': data["scores"],
                           'totalScore': displayScore,
                           'groupSize': round(stage.groupSize, 1),
                           'distance': stage.distance,
                           'timestamp': utc_to_nsw(stage.timestamp).strftime("%d %b %Y %I:%M %p"),
                           'std': round(stage.std, 2),
                           'duration': format_duration(stage.duration),
                           'stageID': stage.id,
                           'sighters': data['sighters']
                           })
    return stagesList, final_page
