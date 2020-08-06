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


from flask import Flask, url_for
from mainServer.auth import permit, authApp
from webPanel.webPanel import *
import flask_login
from bson.objectid import ObjectId

print("main server start")

app = Flask(__name__)
app.secret_key = project_config.secret_key

# flask login manager init

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

# register blueprint of server modules

app.register_blueprint(authApp, url_prefix='/api/auth')
app.register_blueprint(webPanelApp, url_prefix='/webpanel')

# maximum valid upload size

app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024   # max upload size = 128mB

# redirect use to login page

@app.route("/")
def login_page():
    return redirect(url_for('webpanel.login'))

# logout user and redirect back to login page

@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect(url_for('webpanel.login'))

# server start point

def start():
    app.run('127.0.0.1', port=9090, threaded=True)


# return User class for given userid, return null if userid is invalid

@login_manager.user_loader
def load_user(userid):
    print(userid)
    return User(userid, "علیرضا فروزنده نژاد", 'admin')