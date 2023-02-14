from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from app.welcome.email import send_feedback_email

welcome_bp = Blueprint('welcome_bp', __name__)


@welcome_bp.route('/', methods=['GET'])
def index():
    """
    Homepage for the website. Identifies whether person is signed in.

    :return: Index html page
    """
    if not current_user.is_authenticated:
        return redirect(url_for('welcome_bp.landing'))
    if current_user.access == 0:
        return redirect(url_for('profile_bp.profile'))
    return render_template('welcome/index.html')


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

        return redirect(url_for('welcome_bp.index'))
    return render_template('welcome/contact.html')
