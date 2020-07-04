from flask.views import MethodView
from flask import request, current_app, url_for, render_template
from itsdangerous import (
    URLSafeTimedSerializer, SignatureExpired,
    BadTimeSignature, BadSignature
)
from typing import Union
from marshmallow.exceptions import ValidationError
from string import digits, ascii_letters
from base64 import b32encode
import os
import random

from app.utils import db
from ..schemas import ResultSchema, ResultErrorSchema
from ..authentication import require_token, require_admin
from ..role import Role
from ..user.models import User
from .schemas import (
    DaoCreateUserSchema, DaoUpdateUserSchema,
    DaoRequestPasswordResetSchema
)


def random_string(length=16):
    return ''.join(random.choice(ascii_letters + digits) for i in range(length))


class UserResource(MethodView):
    @require_token
    @require_admin
    def get(self, guid: str, **_: dict) -> Union[ResultSchema, ResultErrorSchema]:
        if guid is None:
            return ResultSchema(
                data=[d.jsonify() for d in User.query.all()]
            ).jsonify()
        else:
            data = User.query.filter_by(guid=guid).first()
            if not data:
                return ResultErrorSchema(
                    message='User does not exist!',
                    status_code=404
                ).jsonify()
            return ResultSchema(
                data=data.jsonify()
            ).jsonify()

    @require_token
    @require_admin
    def post(self, **_: dict) -> Union[ResultSchema, ResultErrorSchema]:
        """
        Create an new user account
        """
        schema = DaoCreateUserSchema()
        data = request.get_json() or {}
        try:
            data = schema.load(data)
        except ValidationError as errors:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=errors.messages,
                status_code=400
            ).jsonify()

        # check if the username is already in use
        user_exists = User.query.filter_by(username=data['username']).first()
        if user_exists:
            return ResultErrorSchema(
                message='Username already in use!',
                status_code=422
            ).jsonify()
        # get the role object
        data['role'] = Role.query.filter_by(name=data.get('role')).first()
        if not data['role']:
            return ResultErrorSchema(
                message='Role does not exist!',
                status_code=404
            ).jsonify()

        # create the user and add it to the database
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        return ResultSchema(
            data=user.jsonify(),
            status_code=201
        ).jsonify()

    @require_token
    def put(self, guid: str, user: User, **_: dict) -> Union[ResultSchema, ResultErrorSchema]:
        """
        Modify an existing user account
        """
        if guid == 'me':
            schema = DaoUpdateUserSchema()
            data = request.get_json() or {}
            try:
                data = schema.load(data)
            except ValidationError as errors:
                return ResultErrorSchema(
                    message='Payload is invalid',
                    errors=errors.messages,
                    status_code=400
                ).jsonify()

            if 'role' in data.keys():
                return ResultErrorSchema(
                    message='You are not allowed to change your role!',
                    status_code=403
                ).jsonify()

            totp_secret = None
            totp_deactivation_token = None
            if 'totp_token' in data:
                totp_deactivation_token = data.get('totp_token')
                del data['totp_token']

            for key, val in data.items():
                if key == 'totp_enabled':
                    if val:
                        # generate a new secret
                        if not user.totp_enabled:
                            totp_secret = user.totp_secret = b32encode(os.urandom(10)).decode('utf-8')
                    else:
                        # deactivate 2fa
                        if user.totp_enabled:
                            # if submitted token is valid
                            if not totp_deactivation_token:
                                return ResultErrorSchema(
                                    message='Unable to deactivate 2fa, token not submitted'
                                ).jsonify()
                            if user.verify_totp(totp_deactivation_token):
                                user.totp_enabled = False
                                user.totp_secret = None
                            else:
                                return ResultErrorSchema(
                                    message='Unable to deactivate 2fa, token is invalid'
                                ).jsonify()
                elif key == 'gpg_enabled':
                    if user.gpg_enabled and not val:
                        user.gpg_enabled = False
                else:
                    setattr(user, key, val)

            db.session.commit()
            # if a new secret has been created, add it to the data for 2fa activation process
            data = user.jsonify()
            if totp_secret:
                data['2fa_secret'] = totp_secret
            return ResultSchema(data=data).jsonify()
        else:
            target = User.query.filter_by(guid=guid).first()
            if not target:
                return ResultErrorSchema(
                    message='User does not exist',
                    status_code=404
                ).jsonify()
            return require_admin(self._update_user_as_admin)(user=user, target=target)

    @require_token
    @require_admin
    def delete(self, guid: str, **_: dict):
        """
        Delete an existing account (only with valid guid not with 'me')
        """
        user = User.query.filter_by(guid=guid).first()
        if not user:
            return ResultErrorSchema(
                message='User does not exist',
                status_code=404
            ).jsonify()
        db.session.delete(user)
        db.session.commit()
        return ResultSchema(
            data='Successfully deleted user!',
            status_code=200
        ).jsonify()

    def _update_user_as_admin(self, target: User, **_: dict) -> Union[ResultSchema, ResultErrorSchema]:
        schema = DaoUpdateUserSchema()
        data = request.get_json() or {}
        try:
            data = schema.load(data)
        except ValidationError as errors:
            return ResultErrorSchema(
                message='Payload is invalid',
                errors=errors.messages,
                status_code=400
            ).jsonify()

        for key, val in data.items():
            if key == 'role':
                role = Role.query.filter_by(name=val).first()
                if not role:
                    return ResultErrorSchema(
                        message='Invalid Role',
                        status_code=400
                    ).jsonify()
                else:
                    target.role = role
            elif key == 'totp_enabled':
                if not val:
                    if target.totp_enabled:
                        target.totp_enabled = False
                        target.totp_secret = None
                        target.code_viewed = False
                else:
                    if not target.totp_enabled:
                        return ResultErrorSchema(
                            message='You are not allowed to enable 2FA.'
                        ).jsonify()
            elif key == 'gpg_enabled':
                if not val:
                    if target.totp_enabled:
                        target.gpg_enabled = False
                else:
                    if not target.totp_enabled:
                        return ResultErrorSchema(
                            message='You are not allowed to enable GPG.'
                        ).jsonify()
            else:
                setattr(target, key, val)
        db.session.commit()
        data = target.jsonify()
        return ResultSchema(data=data).jsonify()

