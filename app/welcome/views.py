from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from flask import session as flask_session

from app.models import User
from app.welcome.email import send_feedback_email

welcome_bp = Blueprint('welcome_bp', __name__)


@welcome_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Homepage for the website. Identifies whether person is signed in.

    :return: Index html page
    """
    if not current_user.is_authenticated:
        return redirect(url_for('route_blueprint.landing'))
    if current_user.access == 0:
        return redirect(url_for('.profile'))
    search_error = False
    if request.method == "POST":
        username = request.form['user']
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                flask_session['profileID'] = user.id
                return redirect('/profile')
            else:
                search_error = True
    return render_template('welcome/index.html', error=search_error)


@welcome_bp.route('/landing')
def landing():
    """
    First page opened when address entered

    :return: Landing html page
    """
    return render_template('welcome/landing_page.html')


@welcome_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        feedback = request.form['feedback']
        name = request.form['name']
        if name == '':
            name = "anonymous"
        send_feedback_email(feedback, name)
        flash("Message Sent", "success")

        return redirect(url_for('index'))
    return render_template('welcome/contact.html')