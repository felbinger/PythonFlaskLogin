from flask import (
    Blueprint, render_template,
    request, session, url_for,
    flash, send_from_directory,
    redirect, current_app
)
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import Length, EqualTo
from dateutil.parser import parse
import requests

from .utils import require_login

profile = Blueprint(__name__, 'profile')


class ProfileForm(FlaskForm):
    display_name = StringField('Display Name')
    email = StringField('E-Mail Address')
    username = StringField('Username')
    role = StringField('Role')
    created = StringField('Created')
    last_login = StringField('Last Login')
    enable_2fa = BooleanField('2FA enabled')
    totp_token = StringField('Token to deactivate 2fa')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[Length(min=8)])
    password2 = PasswordField('Password (again)', validators=[EqualTo('password')])


class TokenForm(FlaskForm):
    token = StringField('Token')


@profile.route('/', methods=['GET', 'POST'])
@require_login
def account():
    forms = {
        'modifyProfile': ProfileForm(),
        'changePassword': ChangePasswordForm()
    }

    # todo implement form validation on submit

    header = {'Authorization': f'Bearer {session.get("access_token")}'}
    if request.method == 'POST':
        if request.form is not None:
            action = request.form.get('action')
            if action == 'modifyProfile':
                resp = requests.put(
                    f'{request.scheme}://{request.host}{url_for("user_api")}/me',
                    json={
                        'totp_enabled': request.form.get('enable_2fa') == 'y',
                        'totp_token': request.form.get('totp_token'),
                        'displayName': request.form.get('display_name'),
                        'email': request.form.get('email')
                    },
                    headers=header
                )
                if resp.status_code != 200:
                    flash(f'Unable to update account: {resp.json().get("message")}', 'danger')
                else:
                    if '2fa_secret' in resp.json().get('data'):
                        # @Security: possible security issue
                        session['2fa_secret'] = resp.json().get('data').get('2fa_secret')
                        return redirect(url_for('app.views.profile.enable2fa'))
                    flash(f'Account has been updated!', 'success')

            elif action == 'changePassword':
                password = request.form.get('password')
                if password == request.form.get('password2'):
                    if len(password) < 8:
                        flash('Password is too short!', 'danger')
                    else:
                        resp = requests.put(
                            f'{request.scheme}://{request.host}{url_for("user_api")}/me',
                            headers=header,
                            json={
                                'password': password
                            }
                        )
                        if resp.status_code != 200:
                            flash(f'Unable to update password: {resp.json().get("message")}', 'danger')
                        else:
                            flash('Password has been updated!', 'success')
                else:
                    flash('The entered passwords are not the same!', 'danger')

    role = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers={'Authorization': f'Bearer {session.get("access_token")}'},
    ).json().get('data').get('role').get('name')

    data = requests.get(
        f'{request.scheme}://{request.host}{url_for("auth_api")}',
        headers=header,
    ).json().get('data')
    # reformat timestamps
    data['lastLogin'] = parse(data['lastLogin']).strftime(current_app.config['TIME_FORMAT'])
    data['created'] = parse(data['created']).strftime(current_app.config['TIME_FORMAT'])

    return render_template('index.html', data=data, role=role, forms=forms)


@profile.route('/2fa', methods=['GET', 'POST'])
@require_login
def enable2fa():
    header = {'Authorization': f'Bearer {session.get("access_token")}'}
    form = TokenForm()
    if request.method == 'POST':
        if form.token.data:
            resp = requests.post(
                f'{request.scheme}://{request.host}{url_for("two_factor_api")}',
                headers=header,
                json={
                    'token': form.token.data
                }
            ).json()
            if 'invalid' not in resp.get('message'):
                flash('2FA has been activated', 'success')
            else:
                flash('Invalid Token', 'danger')
        else:
            flash('Invalid Token', 'danger')
        return redirect(url_for('app.views.profile.account'))
    else:
        if '2fa_secret' not in session:
            return redirect(url_for('app.views.profile.account'))
        data = dict()
        data['secret'] = session['2fa_secret']
        del session['2fa_secret']
        data['qr'] = requests.get(
            f'{request.scheme}://{request.host}{url_for("two_factor_api")}',
            headers=header
        ).text
        return render_template('setup2FA.html', data=data, form=form), {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
