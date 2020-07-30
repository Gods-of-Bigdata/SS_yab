from cassandra.cluster import Cluster


class cassandra_api():
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
