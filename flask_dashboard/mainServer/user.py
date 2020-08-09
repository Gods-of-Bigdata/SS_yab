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
from mainServer.auth import *
from bson.objectid import ObjectId
import requests
from bson import json_util
import flask_login

userApp = Blueprint('user', __name__)

# user class for flask-login

class User(flask_login.UserMixin):
    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.role)