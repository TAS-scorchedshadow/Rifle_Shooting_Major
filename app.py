from flask import Flask, render_template
from uploadForms import reportForm

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

if __name__ == '__main__':
    app.run()