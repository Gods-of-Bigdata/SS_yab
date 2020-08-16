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
from clickhouse_driver import Client
from datetime import datetime
from colorama import Fore, Back, Style, init

client = Client('localhost')
# client.execute('DROP TABLE IF EXISTS default.sahamyab')
client.execute('CREATE TABLE IF NOT EXISTS default.sahamyab '
               '('
               'id Int64,'
               'sendTime DateTime,'
               'sendTimePersian String,'
               'hashtags Array(Nullable(String)),'
               'keywords Array(Nullable(String)),'
               'symbols Array(Nullable(String)),'
               'senderUsername String,'
               'senderName String,'
               'content String'
               ')'
               ' ENGINE = MergeTree PARTITION BY toYYYYMMDD(sendTime) ORDER BY toYYYYMMDD(sendTime)')


def handler(message):
    recieved_message = json.loads(message.body)
    data = [[
        int(recieved_message['id']),
        datetime.strptime(recieved_message['sendTime'], '%Y-%m-%dT%H:%M:%SZ'),
        recieved_message['sendTimePersian'],
        recieved_message['hashtags'],
        recieved_message['keywords'],
        recieved_message['symbols'],
        recieved_message['senderUsername'],
        recieved_message['senderName'],
        recieved_message['content']
    ]]
    result = client.execute('INSERT INTO default.sahamyab '
                            '('
                            'id,'
                            'sendTime,'
                            'sendTimePersian,'
                            'hashtags,'
                            'keywords,'
                            'symbols,'
                            'senderUsername,'
                            'senderName,'
                            'content'
                            ')'
                            ' VALUES ', data)
    print(recieved_message['id'])
    message.finish()
    return True


r = nsq.Reader(message_handler=handler,
               lookupd_http_addresses=['http://127.0.0.1:4161'],
               topic='sahamyab_tweets', channel='clickhouse_reader', lookupd_poll_interval=15)

init(autoreset=True)

nsq.run()
