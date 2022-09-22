from app import db


def set_access(user, access_level):
    user.access = access_level
    db.session.commit()


def set_club(user, club):
    user.clubID = club.id
    db.session.commit()


def register_user(form_data, test_client):
    test_client.post('/register', content_type='multipart/form-data', data=form_data)
