from datetime import datetime, timedelta

# copywrite
# Persian date instead of Gregorian


LIFE_TIME = 7 * 24 * 3600


def to_str(n):
    if len(str(n)) == 1:
        return '0' + str(n)
    else:
        return n


def key_date_appendix(sendTime_str):
    # sendTime_str: "2020-07-21T11:04:05Z"
    y = sendTime_str[:4]      # '2020'
    m = sendTime_str[5:7]     # '07'
    d = sendTime_str[8:10]    # '21'
    h = sendTime_str[11:13]   # '11'
    ymdh = y + m + d + h      # '2020072111'
    return ymdh


def key_appendix_datetime(datetime_obj):
    y = datetime_obj.year
    m = datetime_obj.month
    d = datetime_obj.day
    h = datetime_obj.hour
    return str(y) + to_str(m) + to_str(d) + to_str(h)


def user_tweets_count(redis_client, username_str, hours_int=6, now = datetime.now()):
    # number of tweets from hours_int ago til now
    total_tweets = 0

    for hour_offset in range(0, hours_int + 1):
        prev_date = now - timedelta(hours=hour_offset)
        key = "user:" + username_str + ":" + key_appendix_datetime(prev_date)
        if redis_client.exists(key) > 0:
            total_tweets += int(redis_client.get(key).decode("utf-8"))

    return total_tweets


def create_incr_user(redis_client, username_str, sendTime_str):
    key = "user:" + username_str + ":" + key_date_appendix(sendTime_str)
    if redis_client.exists(key) == 0:
        redis_client.set(key, 1, ex=LIFE_TIME)
    else:
        redis_client.incr(key)


def total_tweets_count(redis_client, hours_int=24, now = datetime.now()):
    total_tweets = 0
    
    for hour_offset in range(0, hours_int + 1):
        prev_date = now - timedelta(hours=hour_offset)
        key = "tweets:count:" + key_appendix_datetime(prev_date)
        if redis_client.exists(key) > 0:
            total_tweets += int(redis_client.get(key).decode("utf-8"))

    return total_tweets


def create_incr_tweets_count(redis_client, sendTime_str):
    key = "tweets:count:" + key_date_appendix(sendTime_str)
    if redis_client.exists(key) == 0:
        redis_client.set(key, 1, ex=LIFE_TIME)
    else:
        redis_client.incr(key)


def unique_hashtags_count(redis_client, hours_int=1, now = datetime.now()):
    total_hashtags = 0
    
    for hour_offset in range(0, hours_int + 1):
        prev_date = now - timedelta(hours=hour_offset)
        key = "hashtags:unique:" + key_appendix_datetime(prev_date)
        if redis_client.exists(key) > 0:
            total_hashtags += redis_client.scard(key)

    return total_hashtags


def create_incr_unique_hashtags(redis_client, hashtag_str, sendTime_str):
    key = "hashtags:unique:" + key_date_appendix(sendTime_str)
    if redis_client.exists(key) == 0:
        redis_client.sadd(key, *hashtag_str)
        redis_client.expire(key, LIFE_TIME)
    else:
        redis_client.sadd(key, *hashtag_str)


def create_update_hashtags_list(redis_client, hashtag_str):

    if redis_client.exists("hashtags_list") == 0:
        redis_client.lpush("hashtags_list", *hashtag_str)
        redis_client.expire("hashtags_list", LIFE_TIME)
    else:
        redis_client.lpush("hashtags_list", *hashtag_str)
        if redis_client.llen("hashtags_list") > 1000:    # O(1)
            redis_client.ltrim("hashtags_list", 0, 999)  # O(N+S) N: total #elements, S: offset to H or T
                                                         # So it's better to check first and then trim.


def list_hashtags(redis_client, start = 0, end = -1):
    return [item.decode("utf-8") for item in redis_client.lrange("hashtags_list", start, end)]


def create_update_tweets_list(redis_client, content_str):

    if redis_client.exists("tweets_list") == 0:
        redis_client.lpush("tweets_list", content_str)
        redis_client.expire("tweets_list", LIFE_TIME)
    else:
        redis_client.lpush("tweets_list", content_str)
        if redis_client.llen("tweets_list") > 100:
            redis_client.ltrim("tweets_list", 0, 99)


def list_tweets(redis_client, start = 0, end = -1):
    return [item.decode("utf-8") for item in redis_client.lrange("tweets_list", start, end)]
    


def symbol_tweets_count(redis_client, symbol_str, hours_int=6, now = datetime.now()):  # similar to the user's
    total_tweets = 0
    
    for hour_offset in range(0, hours_int + 1):
        prev_date = now - timedelta(hours=hour_offset)
        key = "symbol:" + symbol_str + ":" + key_appendix_datetime(prev_date)
        if redis_client.exists(key) > 0:
            total_tweets += int(redis_client.get(key).decode("utf-8"))

    return total_tweets


def create_incr_symbol(redis_client, symbol_str, sendTime_str):
    key = "symbol:" + symbol_str + ":" + key_date_appendix(sendTime_str)
    if redis_client.exists(key) == 0:
        redis_client.set(key, 1, ex=LIFE_TIME)
    else:
        redis_client.incr(key)