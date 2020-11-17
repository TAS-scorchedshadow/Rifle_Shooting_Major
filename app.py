from flask import Flask, render_template, request
from uploadForms import reportForm, signInForm

app = Flask(__name__)
app.secret_key = "_wTlFKa92a-UL0GityNmMg"

@app.route('/')
def hello_world():
    return render_template('landingPage.html')


@app.route('/target')
def target_test():
    return render_template('targetTest.html')


@app.route('/profile')
def profile():
    form = reportForm()
    return render_template('students/profile.html',form=form)


@app.route('/user/signin', methods=['GET', 'POST'])
def signin():
    # create form
    form = signInForm()
    # on submission
    if request.method == 'POST':
        if form.validate_on_submit():
            # # Authenticate User. Also initialises sessions.
            # usernameError, passwordError = validateLogin(form)
            # if usernameError or passwordError:
            #     return render_template('signInForm.html', form=form, usernameError=True, passwordError=True)
            # else:
            #     user = User(form.username.data)
            #     login_user(user)
            #     next = flask.request.args.get('next')
            #     # is_safe_url should check if the url is safe for redirects.
            #     # See https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work for an example.
            #     if not is_safe_url(next):
            #         return flask.abort(400)
            #     if current_user.admin == 1:
            #         return flask.redirect('/adminHome')
            #     return flask.redirect(next or flask.url_for('report', username=current_user.username))
            return render_template('landingPage.html')
    return render_template('UserAuth/login.html', form=form)

if __name__ == '__main__':
    app.run()