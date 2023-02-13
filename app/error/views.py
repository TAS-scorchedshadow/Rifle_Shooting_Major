from flask import Blueprint, render_template

error_bp = Blueprint('error', __name__)


@error_bp.route('/403', methods=['GET'])
def user_unauthorised():
    """
    :return: Template for the 403 error page
    """
    return render_template('error/403.html')
