import sqlite3

from flask import flash, redirect, url_for, g
from flask_login import login_user
from flask_login._compat import unicode
from passlib.context import CryptContext
#TODO Ensure that we're not importing from dataAccess. Do all database calls in this file
#from dataAccess import addUser, usernameExists, emailExists, findPassword, initialiseSettings, findID

# -- All work in this security.py is done by Dylan H --


# Password encryption taken from https://blog.tecladocode.com/learn-python-password-encryption-with-flask/
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):  # Checks a string against a stored hashed password returns boolean
    return pwd_context.verify(password, hashed)


def registerUser(form):
    # Assign a new id
    fName = form.fName.data.lower()
    sName = form.sName.data.lower()
    num = 1
    done = False
    while not done:
        assignedID = (fName[0] + "." + sName + str(num))  # Adds 1 to the end of the id
        if usernameExists(assignedID):
            num += 1
        else:
            done = True
    print(assignedID)
    if form.year.data == "None":
        year = null
    else:
        year = form.year.data
    school = form.school.data
    email = form.email.data
    password = form.password.data
    hashedPassword = encrypt_password(password)
    addUser(assignedID, fName, sName, school, email, hashedPassword,year)
    initialiseSettings(assignedID)


def validateLogin(form): #takes a submitted form and checks if the username exsists in the database that has a matching password.
    #Settings defaults
    usernameError = False
    passwordError = False
    #Check if input is a username or email that exists in the database
    if not usernameExists(form.username.data) and not emailExists(form.username.data):
        usernameError = True
    else:
        password = form.password.data
        hashedPassword = findPassword(form.username.data) #Check if password matches
        if not check_encrypted_password(password, hashedPassword):
            passwordError = True
    return usernameError, passwordError


class User():
    def __init__(self,username, active = True):
        self.username = username
        self.active = active

        #TODO change this to fit new database
        conn = sqlite3.connect('PARS.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        result = c.fetchone()
        self.fName = result[2][0].upper() + result[2][1:] #Adds capitalisation to each name
        self.sName = result[3][0].upper() + result[3][1:] #Adds capitalisation to each name
        self.school = result[4]
        self.email = result[5]
        self.admin = result[9]

    def is_authenticated(self):
        return True
        #return true if user is authenticated, provided credentials

    def is_active(self):
        return True
        #return true if user is activte and authenticated

    def is_annonymous(self):
        return False
        #return true if annon, actual user return false

    def get_id(self):
        return unicode(self.username)
        # we are using the username as the ID for this project.
        # get_id defines an id for a user and is used by the user_loader function in app.py
        # to load a user based off their username.

