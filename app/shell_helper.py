from flask import Blueprint

shell_bp = Blueprint('shell_bp', __name__)


def clear_table(db, table):
    items = table.query.all();
    for i in items:
        db.session.delete(i)
    db.session.commit()
    return
