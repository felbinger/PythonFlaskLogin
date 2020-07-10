from flask import Blueprint, render_template, current_app

default = Blueprint('default')


@default.route('/login')
def login():
    return render_template('login.html')


@default.route('/')
def profile():
    return render_template('index.html', date_format=current_app.config['DATE_FORMAT'])


@default.route('/2fa')
def enable2fa():
    return render_template('setup2FA.html'), {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }