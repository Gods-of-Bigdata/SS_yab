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


from flask import Flask, request, abort, Blueprint, jsonify, render_template, redirect, url_for
from mainServer.auth import *
from functools import wraps
import jwt
import hashlib
from bson.objectid import ObjectId
import requests
from bson import json_util
import project_config
import os
import sys
from werkzeug import *
import uuid
from mainServer.user import User
import flask_login
from flask_login import login_required
import shutil
import psutil

webPanelApp = Blueprint('webpanel', __name__, template_folder='templates', static_folder='assets', static_url_path='/assets')


@webPanelApp.route('/')
@webPanelApp.route('/index')
@login_required
def index():
    stat = {}
    #disk_usage = shutil.disk_usage("/root")
    disk_usage = shutil.disk_usage("C:\\")
    stat['disk_total'] = disk_usage.total // (2 ** 20)
    stat['disk_used'] = disk_usage.used // (2 ** 20)
    stat['cpu_used'] = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory()
    stat['ram_used'] = ram_usage.used // (2 ** 20)
    stat['ram_total'] = ram_usage.total // (2 ** 20)
    net_usage = psutil.net_io_counters()
    net_used = net_usage.bytes_recv + net_usage.bytes_sent
    stat['net_used'] = net_used // (2 ** 20)
    return render_template('index.html', stat = stat)


@webPanelApp.route('/searchtweets')
@login_required
def searchtweets():
    return render_template('search.html')

@webPanelApp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')


@webPanelApp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        salted_password = password + project_config.password_salt
        hashed_password = hashlib.sha512(salted_password.encode('utf8')).hexdigest()

        if password != '123': 
            abort(401)

        user = User('123', 'علیرضا فروزنده نژاد', 'admin')
        flask_login.login_user(user)
        return redirect(url_for('webpanel.index'))
