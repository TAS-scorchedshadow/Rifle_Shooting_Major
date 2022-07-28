import json

from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required, current_user

from .functions import get_shoot_data, get_user_dict, get_alert_message, check_usernames, upload_stages, flatten_ids
from .forms import uploadForm

upload_bp = Blueprint('upload_bp', __name__)


@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Page to receive file entries for upload of shoot info

    :return: Upload page html
    """
    # Reroute if invalid user
    if not current_user.access >= 1 or current_user.username == "preview":
        return redirect(url_for('welcome_bp.index'))
    # Initialise Variables
    form = uploadForm()
    template = 'upload/upload.html'
    stage_list = []
    invalid_list = []
    alert = [None, 0, 0]  # Alert type, Failures, Successes
    if form.identifier.data == "upload":
        # Upload
        if request.method == "POST":
            # Process files, then make front end information
            stage_list, invalid_list, count = get_shoot_data(form)
            template, alert = get_alert_message("upload", count)
    else:
        # Verify
        # Get data from forms
        stage_list = json.loads(request.form["stageDump"])
        stage_define = {'location': form.location.data, 'weather': form.weather.data, 'ammoType': form.ammoType.data}
        user_dict = get_user_dict()
        # Upload stages, then make front end information
        stage_list, invalid_list, invalid_list_id, fail_count = check_usernames(stage_list, user_dict)
        count = upload_stages(stage_list, invalid_list_id, stage_define, user_dict)
        count["failure"] = fail_count
        template, alert = get_alert_message("verify", count)
        if alert[0] == "Incomplete":
            stage_list = flatten_ids(invalid_list)
    # Dump stage_list and render
    stageDump = json.dumps(stage_list)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalid_list, alert=alert)
