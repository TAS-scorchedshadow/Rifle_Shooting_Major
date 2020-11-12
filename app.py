from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('landingPage.html')

@app.route('/target')
def target_test():
    return render_template('targetTest.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run()
