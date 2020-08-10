from cassandra.cluster import Cluster
from datetime import datetime, timedelta

# copywrite
# Persian date instead of Gregorian
LIFE_TIME = 7 * 24 * 3600

def key_date_appendix(sendTime_str):
    # sendTime_str: "2020-07-21T11:04:05Z"
    y = sendTime_str[:4]      # '2020'
    m = sendTime_str[5:7]     # '07'
    d = sendTime_str[8:10]    # '21'
    h = sendTime_str[11:13]  # '11'
    mnt = sendTime_str[14:16]
    dlt = timedelta(hours=4,minutes=30)
    dt = datetime(int(y),int(m),int(d),int(h),int(mnt))+ dlt
    ymdh = ''.join(filter(str.isdigit, dt.__str__()))[:-4]     # '2020072111'
    return ymdh

def key_appendix_datetime(datetime_obj):
    dlt = timedelta(hours=4,minutes=30)
    datetime_obj = datetime_obj + dlt
    y = datetime_obj.year
    m = datetime_obj.month
    d = datetime_obj.day
    h = datetime_obj.hour
    
    return '{}{:02d}{:02d}{:02d}'.format(y,m,d,h)

def getPersianTime(flaskDict):
    try:
        start_date = '13{:02d}/{:02d}/{:02d} {:02d}:00'.format(flaskDict['sY'],
                                                               flaskDict['sM'],
                                                               flaskDict['sD'],
                                                               flaskDict['sH'])
        end_date = '13{:02d}/{:02d}/{:02d} {:02d}:00'.format(flaskDict['eY'],
                                                               flaskDict['eM'],
                                                               flaskDict['eD'],
                                                               flaskDict['eH'])
        return start_date,end_date,True
    except:
        return False,False,False
    
def elasticQuery(es_client,result_set):
    output = []
    q = {
      "query": {
        "match": {
          "id": "134606099"
            }
          }
        }
    for row in result_set:  
        q['query']['match']['id'] = row.id
        try:
            response = es_client.search(index = 'stock_tweets', body = q)['hits']['hits'][0]['_source']
            response['keywords'] = ', '.join(response['keywords'])
            response['symbols'] = ', '.join(response['symbols'])
            output.append(response)
        except:
            pass
    return output


#%%
class redisApi():
    def __init__(self,redis_client):
        self.redis_client = redis_client
            
    def user_tweets_count(self,username_str, hours_int=6, now = datetime.now()):
        if type(hours_int) != int:
            hours_int = int(hours_int)
        # number of tweets from hours_int ago til now
        total_tweets = 0
    
        for hour_offset in range(0, hours_int + 1):
            prev_date = now - timedelta(hours=hour_offset)
            key = "user:" + username_str + ":" + key_appendix_datetime(prev_date)
            if self.redis_client.exists(key) > 0:
                total_tweets += int(self.redis_client.get(key).decode("utf-8"))
    
        return total_tweets
    
    
    def create_incr_user(self, username_str, sendTime_str):
        key = "user:" + username_str + ":" + key_date_appendix(sendTime_str)
        if self.redis_client.exists(key) == 0:
            self.redis_client.set(key, 1, ex=LIFE_TIME)
        else:
            self.redis_client.incr(key)
    
    #%%
    def total_tweets_count(self, hours_int=24, now = datetime.now()):
        if type(hours_int) != int:
            hours_int = int(hours_int)
        total_tweets = 0
        
        for hour_offset in range(0, hours_int + 1):
            prev_date = now - timedelta(hours=hour_offset)
            key = "tweets:count:" + key_appendix_datetime(prev_date)
            if self.redis_client.exists(key) > 0:
                total_tweets += int(self.redis_client.get(key).decode("utf-8"))
    
        return total_tweets
    
    
    def create_incr_tweets_count(self, sendTime_str):
        key = "tweets:count:" + key_date_appendix(sendTime_str)
        if self.redis_client.exists(key) == 0:
            self.redis_client.set(key, 1, ex=LIFE_TIME)
        else:
            self.redis_client.incr(key)
    
    
    def create_update_tweets_list(self, content_str):
    
        if self.redis_client.exists("tweets_list") == 0:
            self.redis_client.lpush("tweets_list", content_str)
            self.redis_client.expire("tweets_list", LIFE_TIME)
        else:
            self.redis_client.lpush("tweets_list", content_str)
            if self.redis_client.llen("tweets_list") > 100:
                self.redis_client.ltrim("tweets_list", 0, 99)
    
    
    def list_tweets(self, start = 0, end = -1):
        return [item.decode("utf-8") for item in self.redis_client.lrange("tweets_list", start, end)]
        
    #%%
    
    def unique_keywords_count(self, hours_int=1, now = datetime.now()):
        if type(hours_int) != int:
            hours_int = int(hours_int)
        total_keywords = 0
        
        for hour_offset in range(0, hours_int + 1):
            prev_date = now - timedelta(hours=hour_offset)
            key = "keywords:unique:" + key_appendix_datetime(prev_date)
     
            if self.redis_client.exists(key) > 0:
                total_keywords += self.redis_client.scard(key)
    
        return total_keywords
    
    
    def create_incr_unique_keywords(self, keyword_str, sendTime_str):
        key = "keywords:unique:" + key_date_appendix(sendTime_str)

        if self.redis_client.exists(key) == 0:
            self.redis_client.sadd(key, *keyword_str)
            self.redis_client.expire(key, LIFE_TIME)
        else:
            self.redis_client.sadd(key, *keyword_str)
    
    
    def create_update_keywords_list(self, keyword_str):
    
        if self.redis_client.exists("keywords_list") == 0:
            self.redis_client.lpush("keywords_list", *keyword_str)
            self.redis_client.expire("keywords_list", LIFE_TIME)
        else:
            self.redis_client.lpush("keywords_list", *keyword_str)
            if self.redis_client.llen("keywords_list") > 1000:    # O(1)
                self.redis_client.ltrim("keywords_list", 0, 999)  # O(N+S) N: total #elements, S: offset to H or T
                                                             # So it's better to check first and then trim.
    
    
    def list_keywords(self, start = 0, end = -1):
        return [item.decode("utf-8") for item in self.redis_client.lrange("keywords_list", start, end)]

    def symbol_tweets_count(self, symbol_str, hours_int=6, now = datetime.now()):  # similar to the user's
        if type(hours_int) != int:
            hours_int = int(hours_int)    
        total_tweets = 0
        
        for hour_offset in range(0, hours_int + 1):
            prev_date = now - timedelta(hours=hour_offset)
            key = "symbol:" + symbol_str + ":" + key_appendix_datetime(prev_date)
            if self.redis_client.exists(key) > 0:
                total_tweets += int(self.redis_client.get(key).decode("utf-8"))
    
        return total_tweets
    
    
    def create_incr_symbol(self, symbol_str, sendTime_str):
        key = "symbol:" + symbol_str + ":" + key_date_appendix(sendTime_str)
        if self.redis_client.exists(key) == 0:
            self.redis_client.set(key, 1, ex=LIFE_TIME)
        else:
            self.redis_client.incr(key)
            
    def create_update_symbols_list(self, symbol_str):
    
        if self.redis_client.exists("symbols_list") == 0:
            self.redis_client.lpush("symbols_list", symbol_str)
            self.redis_client.expire("symbols_list", LIFE_TIME)
        else:
            self.redis_client.lpush("symbols_list", symbol_str)
            if self.redis_client.llen("symbols_list") > 100:
                self.redis_client.ltrim("symbols_list", 0, 99)
    
    
    def list_symbols(self, start = 0, end = -1):
        return [item.decode("utf-8") for item in self.redis_client.lrange("symbols_list", start, end)]  

    def redist_insert(self,recieved_message):
        self.create_incr_user(recieved_message["senderUsername"], recieved_message["sendTime"])
        self.create_incr_tweets_count(recieved_message["sendTime"])
        if "" not in recieved_message["keywords"] and len(recieved_message["keywords"]) != 0:
            self.create_incr_unique_keywords(recieved_message["keywords"], recieved_message["sendTime"])
            self.create_update_keywords_list(recieved_message["keywords"])
        
        self.create_update_tweets_list(recieved_message["content"])
        
        if "" not in recieved_message["symbols"] and len(recieved_message["symbols"]) != 0:
            for symbol in recieved_message["symbols"]:
                self.create_incr_symbol(symbol, recieved_message["sendTime"])    
                self.create_update_symbols_list(symbol)

    def redis_query(self,flaskDict):
        user_posts_count = self.user_tweets_count(flaskDict['username'], hours_int=flaskDict['userRange'])
        symbol_posts_count = self.symbol_tweets_count(flaskDict['symbol'], hours_int=flaskDict['symbolRange'])
        all_posts_count = self.total_tweets_count(hours_int=flaskDict['postRange'])
        keyword_unique_count = self.unique_keywords_count(hours_int=flaskDict['keywordRange'])
    
        counts = {'userPostsCount':user_posts_count,
                'symbolPostsCount':symbol_posts_count,
                'allPostsCount':all_posts_count,
                'keywordUniqueCount':keyword_unique_count,
                }
        return counts

    def redis_list(self):
        keyword_list = self.list_keywords()
        post_list = self.list_tweets()
        lists = {'keywordList':keyword_list,
                'postList':post_list
                }
        return lists
#%%
class CassandraApi:
    def __init__(self, KEYSPACE):

        self.KEYSPACE = KEYSPACE
        cluster = Cluster()
        self.session = cluster.connect()

        self.session.execute("""
                CREATE KEYSPACE IF NOT EXISTS %s
                WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                """ % self.KEYSPACE)

        self.session.set_keyspace(self.KEYSPACE)

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS %s (
                user text,
                
                hour text,
                day text,
                month text,
                year text,
                id text,
                timePersian text,
                PRIMARY KEY ((year,month),day,hour,user)
            )
            """ % 'posts')

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS %s (
                user text,
                
                id text,
                timePersian text,
                PRIMARY KEY (user,timePersian)
            )
            """ % 'users')

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS %s (
                symbol text, 
                user text,
                
                id text,
                timePersian text,
                PRIMARY KEY (symbol,timePersian,user)
            )
            """ % 'symbols')

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS %s (
                keyword text,
                user text,
                
                id text,
                timePersian text,
                PRIMARY KEY (keyword,timePersian,user)
            )
            """ % 'keywords')

    def insertRow(self, table, val_dict):

        keys = list(val_dict.keys())
        values = tuple(val_dict.values())

        insert_st = ("INSERT INTO {} ({}) "
                     .format(table, ','.join(['{}'] * len(keys)))
                     .format(*keys))
        values_st = ("VALUES ({})"
                     .format(','.join(['{}'] * len(keys)))
                     .format(*['%s'] * len(keys)))
        query = insert_st + values_st
        self.session.execute(query, values)

    def insertTweet(self, tweet):
        userName = tweet['senderUsername']
        _id = tweet['id']
        symbols = tweet['symbols']
        keywords = tweet['keywords']
        hashtags = tweet['hashtags']
        timePersian = tweet['sendTimePersian']

        persian_spit = timePersian.split()
        hour = persian_spit[1][:2]
        year, month, day = tuple(persian_spit[0].split('/'))

        self.insertRow('posts', {'user': userName,
                                 'year': year, 'month': month, 'day': day, 'hour': hour,
                                 'id': _id, 'timePersian': timePersian
                                 })

        self.insertRow('users', {'user': userName,
                                 'id': _id, 'timePersian': timePersian
                                 })

        for symbol in symbols:
            self.insertRow('symbols', {'user': userName,
                                       'symbol': symbol,
                                       'id': _id, 'timePersian': timePersian
                                       })

        for keyword in keywords:
            self.insertRow('keywords', {'user': userName,
                                        'keyword': keyword,
                                        'id': _id, 'timePersian': timePersian
                                        })
    def cassandraQuery(self,flaskDict):
        table_name = flaskDict['table']
        
        start_date,end_date,ret = getPersianTime(flaskDict)
        
        if table_name.lower() == 'posts':
            year,month,day,hour = (flaskDict['sY'],flaskDict['sM'],flaskDict['sD'],flaskDict['sH'])
            year = '13'+year
            if year and month and day and hour:
                qry = "SELECT * FROM %s WHERE year = '%s' and month = '%s' \
                    and day = '%s' and hour = '%s'" % (table_name,year,month,day,hour)
            elif year and month and day:
                qry = "SELECT * FROM %s WHERE year = '%s' and month = '%s' \
                    and day = '%s'" % (table_name,year,month,day)
            elif year and month:
                qry = "SELECT * FROM %s WHERE year = '%s' and month = '%s' " % (table_name,year,month)            
        
        elif table_name.lower() == 'users':
            user_name = flaskDict['username']
            if ret:
                qry = "SELECT * FROM %s WHERE user = '%s' \
                        and timepersian > '%s' \
                        and timepersian < '%s'" %   (table_name,user_name,
                                                    start_date,end_date)
            else:      
                qry = "SELECT * FROM %s WHERE user = '%s' " % (table_name,user_name)
        
        elif table_name.lower() == 'symbols':
            symbol_name = flaskDict['symbol']
            if ret:
                qry = "SELECT * FROM %s WHERE symbol = '%s' \
                        and timepersian > '%s' \
                        and timepersian < '%s'" %   (table_name,symbol_name,
                                                    start_date,end_date)
            else:      
                qry = "SELECT * FROM %s WHERE symbol = '%s' " % (table_name,symbol_name)   
                
        elif table_name.lower() == 'keywords':
            keyword_name = flaskDict['keyword']
            if ret:
                qry = "SELECT * FROM %s WHERE symbol = '%s' \
                        and timepersian > '%s' \
                        and timepersian < '%s'" %   (table_name,keyword_name,
                                                    start_date,end_date)
            else:      
                qry = "SELECT * FROM %s WHERE keyword = '%s' " % (table_name,keyword_name)               
        result_set = self.session.execute(qry)
        return list(result_set)
    
    
if __name__ == '__main__':
    from redis.client import Redis

    redis_client = Redis("localhost", port=6379)
    redis_api = redisApi(redis_client)
    qq = redis_api.redisQuery
  