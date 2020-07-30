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

import requests
import json
import time
from colorama import Fore, Back, Style, init
from preprocess import sahamyab_preprocess


class SahamYabAdapter:
    def __init__(self, API_URL='https://www.sahamyab.com/guest/twiter/list?v=0.1', MAX_TWEET_ID=915269688):
        self.API_URL = API_URL
        self.req_obj = {"page": 1, "id": str(MAX_TWEET_ID)}

    def _req_last_tweets(self):
        response = requests.post(self.API_URL, data=self.req_obj)
        return json.loads(response.text)

    def wait_for_tweets(self, callback, fetch_interval=0.3):
        last_tweet_id = 0
        while True:
            tweets = self._req_last_tweets()['items']
            batch_max_tweet = 0
            for tweet in tweets:
                tweet_id = int(tweet['id'])
                if tweet_id > last_tweet_id:
                    callback(tweet)
                if tweet_id > batch_max_tweet:
                    batch_max_tweet = tweet_id
            last_tweet_id = batch_max_tweet
            time.sleep(fetch_interval)


class NSQ_Writer:
    def __init__(self, server='http://127.0.0.1:4151'):
        self.server = server

    def pub(self, channel, message):
        response = requests.post('{}/pub?topic={}'.format(self.server, channel), data=message)
        return response


sahamyab = SahamYabAdapter()
nsq = NSQ_Writer()
process = sahamyab_preprocess()
init(autoreset=True)

# main loop
print('\t Waiting for tweets ...')


def handle_tweet(tweet):
    print('{}[Producer]{} Tweet Id: {}, Username: {}'.format(Fore.GREEN, Fore.WHITE, tweet['id'],
                                                             tweet['senderUsername']))
    message = process.get_compelete_json(tweet)
    return nsq.pub(channel='sahamyab_tweets', message=json.dumps(message))


sahamyab.wait_for_tweets(handle_tweet)