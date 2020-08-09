# Copyright (C) 2020  Gods of Bigdata - Alireza Forouzandeh Nezhad -- afn7991@gmail.com 
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from flask import Flask, request, abort, Blueprint, jsonify
from functools import wraps
import jwt
import hashlib
import project_config
from bson import json_util


authApp = Blueprint('auth', __name__)

# Python decorator for checking permission in request

def permit(*permitted_users):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json_object = request.get_json()
            try:
                decoded_token = jwt.decode(json_object['auth'], project_config.secret_key, algorithms='HS256')
            except:
                return json_util.dumps({
                    'success': False,
                    'msg': 'bad token'
                })
            print('user role : ' + decoded_token['role'])
            if decoded_token['role'] not in permitted_users:
                return json_util.dumps({
                    'success': False,
                    'msg': 'permission denied for this user'
                })
            print('permitted ')
            return func(*args, **kwargs)
        return wrapper
    return decorator


# get userid from given jwt auth token

def get_user_id(json_object):
    try:
        decoded_token = jwt.decode(json_object['auth'], project_config.secret_key, algorithms='HS256')
        return decoded_token['_id']
    except:
        pass


# get user role from given jwt auth token

def get_user_role(json_object):
    try:
        decoded_token = jwt.decode(json_object['auth'], project_config.secret_key, algorithms='HS256')
        return decoded_token['role']
    except:
        pass


# @API: Authenticate user and return jwt token
#
# - Inputs:   email
#           password
# - Output:   success
#           auth (token)

@authApp.route('/get', methods=['GET','POST'])
def get_auth_token():
    json_obj = request.get_json()
    email = json_obj['email']
    password = json_obj['password']
    salted_password = password + project_config.password_salt
    hashed_password = hashlib.sha512(salted_password.encode('utf8')).hexdigest()

    payload = {
        '_id': '123',
        'role': 'admin'
    }

    encoded_auth_token = jwt.encode(payload, project_config.secret_key, algorithm='HS256')
    return jsonify({
        'success': True,
        'auth': encoded_auth_token.decode('ascii')
    })


# @API: Validate given auth token
#
# - Inputs:   auth (token)
# - Output:   success / decoded token


@authApp.route('/validate', methods=['GET', 'POST'])
def validate_auth_token():
    json_object = request.get_json()
    try:
        decoded_token = jwt.decode(json_object['auth'], project_config.secret_key, algorithms='HS256')
        return str(decoded_token)
    except:
        return json_util.dumps({
            'success': False,
            'msg': 'invalid token'
        })


