from flask import request

from app import db
from app.models import User, Stage, Shot, Settings

from .decompress import read_archive
from .upload_processing import validate_shots
from .email import send_upload_email


def get_shoot_data(form):
    """
    Reads all uploaded files and outputs a list of all stages, a list of invalid stages, and a dictionary
    recording the number of stages read

    | Returns the following variables:
    | stage_list: A list of stage dictionaries
    | invalid_list: A list of stage dictionaries which are missing a valid username
    | count: A dictionary containing total and successful uploads

    :param form: form class for the upload page
    :return: stage_list, invalid_list, count
    """
    stage_list = []
    invalid_list = []
    count = {"total": 0, "failure": 0, "success": 0}
    files = form.file.data
    upload_time = int(form.weeks.data)
    for file in files:
        stages = read_archive(file, upload_time)
        for stage_dict, issue_code in stages:
            if 2 not in issue_code:                 # Error code 2: at least more than 1 counting shot
                stage = validate_shots(stage_dict)  # Reformat shoot stage to obtain usable data
                stage['listID'] = count["total"]
                stage_list.append(stage)
                if 1 in issue_code:                 # Error code 1: missing username
                    invalid_list.append(stage)
                else:
                    count["success"] += 1
                count["total"] += 1
    return stage_list, invalid_list, count


def flatten_ids(stage_list):
    """
    Flattens a stage list, removing all number gaps between list IDs.

    :param stage_list: Stage list to be flattened
    :type stage_list: list[dict]
    :return: Flattened stage list
    """
    count = 0
    for item in stage_list:
        item["listID"] = count
        count += 1
    return stage_list


def get_user_dict():
    """
    Gets all users within the database and places them into a dictionary

    :return: Dictionary of users
    """
    user_list = [user for user in User.query.all()]
    user_dict = {}
    for user in user_list:
        user_dict[user.username] = user.id
    return user_dict


def check_usernames(stage_list, user_dict):
    """
    Updates the usernames associated with stages on the verify page.
    If a valid username was not input, it is returned in the invalid list.

    | Returns the following variables:
    | stage_list: A list of stage dictionaries
    | invalid_list: A list of stage dictionaries which are missing a valid username
    | invalid_list_id: A list of ids of stages in the invalid list
    | fail_count: An integer counting the number of still invalid usernames

    :param stage_list: list of stage dictionaries
    :type stage_list: list[dict]
    :param user_dict: dictionary of users
    :type user_dict: dict[str, str]
    :return: stage_list, invalid_list, invalid_list_id, fail_count
    """
    invalid_list = []
    invalid_list_id = []
    fail_count = 0
    for key in request.form:
        if "username." in key:
            username = request.form[key]
            stage_list[int(key[9:])]['username'] = username
            if username not in user_dict:
                invalid_list.append(stage_list[int(key[9:])])
                invalid_list_id.append(int(key[9:]))
                fail_count += 1
    return stage_list, invalid_list, invalid_list_id, fail_count


def upload_stages(stage_list, invalid_list_id, stage_define, user_dict):
    """
    Uploads valid stages, then sends an email to users if the option is set

    :param stage_list: list of all stages
    :type stage_list: list[dict]
    :param invalid_list_id: list of invalid ids of all stages
    :type invalid_list_id: list[int]
    :param stage_define: dictionary for fields that must be user-defined
    :type stage_define: dict
    :param user_dict: dictionary of all users
    :type user_dict: dict[str, str]
    :return: count: dictionary counting successfully uploaded stages, and total stages in stage_list
    """
    count = {"total": 0, "failure": 0, "success": 0}
    stageClassList = []
    for item in stage_list:
        if item['listID'] not in invalid_list_id:
            # Uploads a stage
            # todo: Need to add an ammoType column to the stage database
            print(item['username'])
            stage = Stage(id=item['id'], userID=user_dict[item['username']],
                          timestamp=item['time'],
                          groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                          distance=item['distance'], location=stage_define['location'],
                          notes="")
            db.session.add(stage)
            stageClassList.append(stage)
            # Uploads all shots in the stage
            for point in item['validShots']:
                shot = Shot(stageID=item['id'], timestamp=point['ts'],
                            xPos=point['x'], yPos=point['y'],
                            score=point['score'], vScore=point['Vscore'],
                            sighter=point['sighter'])
                db.session.add(shot)
            print('ready for upload')
            count["success"] += 1
        count["total"] += 1
    db.session.commit()
    for user in User.query.all():
        print(user)
        print(stageClassList)
        s = Settings.query.filter_by(id=0).first()
        if s.email_setting == 2:
            send_upload_email(user, stageClassList)
    return count


def get_alert_message(page, count):
    """
    Gets the relevant page template and alert message given relevant parameters

    | Returns the following variables:
    | template: A html template for what page to display
    | alert: A list containing a string for what message to send, and two integers for counts relevant to the message.

    :param page: String to determine whether the current page is the upload page or the verify page
    :type page: str
    :param count: Dictionary of success, total and fail counts
    :type count: dict
    :return: template, alert
    """
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    template = 'upload/upload.html'
    if page == "upload":
        # Alert message handling
        template = 'upload/upload_verify.html'
        if count["success"] > 0:
            alert[0] = "Success"
            alert[2] = count["success"]
        if count["failure"] > 0 or count["total"] == 0:
            alert[0] = "Warning"
            alert[1] = count["failure"]
            if count["failure"] == count["total"]:
                # If ALL files failed, return to upload page
                template = 'upload/upload.html'
                alert[0] = "Failure"
    if page == "verify":
        # Verify message handling
        if count["success"] == count["total"]:          # successfully uploaded
            alert[0] = "Success"
            alert[2] = count["success"]
        else:                                           # Failed to upload
            template = 'upload/upload_verify.html'
            alert[0] = "Incomplete"
            alert[1] = count["failure"]
            alert[2] = count["success"]
            print("DEBUG: Not all usernames correct")
    return template, alert
