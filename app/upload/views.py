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

    :return: Upload html page
    """
    # Initialise Variables
    if not current_user.access >= 1 or current_user.username == "preview":
        return redirect(url_for('index'))
    form = uploadForm()
    if form.identifier.data == "upload":
        # Upload
        template = 'upload/upload_verify.html'
        stage_list, invalid_list, count = get_shoot_data(form)
        template, alert = get_alert_message("upload", count)
    else:
        # Verify
        stage_list = json.loads(request.form["stageDump"])
        stage_define = {'location': form.location.data, 'weather': form.weather.data, 'ammoType': form.ammoType.data}
        user_dict = get_user_dict()
        stage_list, invalid_list, invalid_list_id, fail_count = check_usernames(stage_list, user_dict)
        count = upload_stages(stage_list, invalid_list_id, stage_define, user_dict)
        count["failure"] = fail_count
        template, alert = get_alert_message("verify", count)
        if alert[0] == "Incomplete":
            stage_list = flatten_ids(invalid_list)
    stageDump = json.dumps(stage_list)
    return render_template(template, form=form, stageDump=stageDump, invalidList=invalid_list, alert=alert)