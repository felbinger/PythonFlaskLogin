from flask import Blueprint, render_template, request, session, url_for, current_app
from dateutil.parser import parse
import requests

from .utils import require_login

default = Blueprint(__name__, 'default')


@default.route('/', methods=['GET', 'POST'])
@require_login
def profile():
    data = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers={'Authorization': f'Bearer {session.get("access_token")}'},
    ).json().get('data')
    # reformat timestamps
    data['lastLogin'] = parse(data['lastLogin']).strftime(current_app.config['TIME_FORMAT'])
    data['created'] = parse(data['created']).strftime(current_app.config['TIME_FORMAT'])
    return render_template('index.html', data=data, role=data.get('role').get('name'))


@default.route('/2fa', methods=['GET'])
@require_login
def enable2fa():
    return render_template('setup2FA.html'), {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
