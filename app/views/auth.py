from flask import (
    Blueprint, render_template,
    request, session,
    url_for
)
import requests

from .utils import require_login, require_logout

auth = Blueprint(__name__, 'auth')


@auth.route('/login', methods=['GET', 'POST'])
@require_logout
def login():
    if request.method == 'POST':
        if 'accessToken' in request.get_json() and 'refreshToken' in request.get_json():
            access_token = request.get_json().get('accessToken')
            resp = requests.get(
                f'{request.scheme}://{request.host}{url_for("auth_api")}',
                headers={'Authorization': f'Bearer {access_token}'},
            )
            if resp.status_code == 200:
                session['access_token'] = access_token
                session['refresh_token'] = request.get_json().get('refreshToken')
                return 'Success', 200
            else:
                return 'Access Token is invalid', 401
        else:
            return 'Payload is invalid', 400
    return render_template('login.html')


@auth.route('/logout', methods=['POST'])
@require_login
def logout():
    session['refresh_token'] = None
    session['access_token'] = None
    return 'Success', 200

