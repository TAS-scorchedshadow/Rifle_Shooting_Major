# By Dylan Huynh
from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required, current_user

from app.models import Stage, User
from app.stages_calc import plotsheet_calc

plotsheet_bp = Blueprint('plotsheet_bp', __name__)

@login_required
@plotsheet_bp.route('/target')
def target():
    """
    Displays target & mapping of shots from the shoot

    :return:
    """
    # This route takes an argument from url and uses it to query the database for
    # the relevant shots and range information
    stageID = request.args.get('stageID')
    stage = Stage.query.filter_by(id=stageID).first()
    if stage:
        user = User.query.filter_by(id=stage.userID).first()
        data = plotsheet_calc(stage, user)
        if current_user.access >= 1:
            return render_template('plotsheet/plotsheet.html', data=data, user=user, stage=stage)
        else:
            return render_template('plotsheet/student_plot_sheet.html', data=data, user=user, stage=stage)
    return redirect(url_for('welcome.index'))