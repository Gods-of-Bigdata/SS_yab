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
import redis
from colorama import Fore, Back, Style, init
from cassandra_database import CassandraApi
from redis.client import Redis
from elasticsearch import Elasticsearch
from redis_funcs import *
from datetime import datetime, timedelta


cassandra_db = CassandraApi('sahamyab')
redis_client = Redis("localhost", port=6379)
es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def handler(message):
    recieved_message = json.loads(message.body)
    # Cassandra
    cassandra_db.insertTweet(recieved_message)
    
    # ES & K
    es_client.index(index = 'stock_tweets', id = recieved_message["id"], body = recieved_message)
    
    # Redis
    create_incr_user(redis_client, recieved_message["senderUsername"], recieved_message["sendTime"])
    create_incr_tweets_count(redis_client, recieved_message["sendTime"])
    if "" not in recieved_message["hashtags"] and len(recieved_message["hashtags"]) != 0:
        create_incr_unique_hashtags(redis_client, recieved_message["hashtags"], recieved_message["sendTime"])
        create_update_hashtags_list(redis_client, recieved_message["hashtags"])
    
    create_update_tweets_list(redis_client, recieved_message["content"])
    
    if "" not in recieved_message["symbols"] and len(recieved_message["symbols"]) != 0:
        for symbol in recieved_message["symbols"]:
            create_incr_symbol(redis_client, symbol, recieved_message["sendTime"])    


    print('{}[Consumer]{} Tweet Id: {}, Username: {}'.format(Fore.YELLOW, Fore.WHITE, recieved_message['id'],
                                                             recieved_message['senderUsername']))
    message.finish()
    return True


r = nsq.Reader(message_handler=handler,
               lookupd_http_addresses=['http://127.0.0.1:4161'],
               topic='sahamyab_tweets', channel='example_reader', lookupd_poll_interval=15)

init(autoreset=True)

nsq.run()
