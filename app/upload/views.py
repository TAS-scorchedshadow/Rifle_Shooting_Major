import json

from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required, current_user

from app import db
from app.models import User, Stage, Shot, Settings

from .decompress import read_archive
from .forms import uploadForm
from .upload_processing import validate_shots
from .email import send_upload_email

upload_bp = Blueprint('upload_bp', __name__)


@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Page to receive file entries for upload of shoot info

    :return: Upload html page
    """
    # Initialise Variables
    if not current_user.access >= 1 or current_user.username == "preview":
        return redirect(url_for('index'))
    form = uploadForm()
    stage_list = []
    invalid_list = []
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    count = {"total": 0, "failure": 0, "success": 0}
    template = 'upload/upload.html'
    if form.identifier.data == "upload":
        # Uploading
        if request.method == "POST":
            template = 'upload/upload_verify.html'
            files = form.file.data
            upload_time = int(form.weeks.data)
            for file in files:
                stages = read_archive(file, upload_time)
                for stage_dict, issue_code in stages:
                    if 2 not in issue_code:  # i.e. at least more than 1 counting shot
                        stage = validate_shots(stage_dict)  # Reformat shoot stage to obtain usable data
                        stage['listID'] = count["total"]
                        stage_list.append(stage)
                        if 1 in issue_code:  # i.e. missing username
                            invalid_list.append(stage)
                        else:
                            count["success"] += 1
                        count["total"] += 1

            # Alert message handling
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
    else:
        # Verifying Upload
        stage_list = json.loads(request.form["stageDump"])
        stage_define = {'location': form.location.data, 'weather': form.weather.data, 'ammoType': form.ammoType.data}
        invalid_list_id = []
        user_list = [user for user in User.query.all()]
        user_dict = {}
        for user in user_list:
            user_dict[user.username] = user.id
        for key in request.form:
            if "username." in key:
                username = request.form[key]
                stage_list[int(key[9:])]['username'] = username
                if username not in user_dict:
                    invalid_list.append(stage_list[int(key[9:])])
                    invalid_list_id.append(int(key[9:]))
                    count["failure"] += 1
        print('started')
        print(invalid_list_id)
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
        print("DEBUG: Completed Upload")
        if count["success"] == count["total"]:  # successfully uploaded
            stageClassList = []
            for item in stage_list:
                stage = Stage(id=item['id'], userID=user_dict[item['username']],
                              timestamp=item['time'],
                              groupSize=item['groupSize'], groupX=item['groupX'], groupY=item['groupY'],
                              distance=item['distance'], location=stage_define['location'],
                              notes="")
                stageClassList.append(stage)
            for user in user_list:
                print(user)
                print(stageClassList)
                s = Settings.query.filter_by(id=0).first()
                if s.email_setting == 2:
                    send_upload_email(user, stageClassList)
            stage_list = []
            alert[0] = "Success"
            alert[2] = count["success"]
        else:  # Failed to upload
            stage_list = invalid_list
            count["total"] = 0
            for item in stage_list:
                item["listID"] = count["total"]
                count["total"] += 1
            template = 'upload/upload_verify.html'
            alert[0] = "Incomplete"
            alert[1] = count["failure"]
            alert[2] = count["success"]
            print("DEBUG: Not all usernames correct")
    stageDump = json.dumps(stage_list)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalid_list, alert=alert)
