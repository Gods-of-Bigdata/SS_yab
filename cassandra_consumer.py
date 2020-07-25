# Copyright (C) 2020  Gods of Bigdata
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

import nsq
import json
from colorama import Fore, Back, Style, init
from cassandra_database import cassandra_api
cassandra_db = cassandra_api('sahamyab')
def handler(message):
    recieved_message = json.loads(message.body)
    cassandra_db.insertTweet(recieved_message)
    print('{}[Consumer]{} Tweet Id: {}, Username: {}'.format(Fore.YELLOW, Fore.WHITE, recieved_message['id'], recieved_message['senderUsername']))
    message.finish()
    return True

r = nsq.Reader(message_handler=handler,
        lookupd_http_addresses=['http://127.0.0.1:4161'],
        topic='sahamyab_tweets', channel='example_reader', lookupd_poll_interval=15)

init(autoreset=True)

nsq.run()