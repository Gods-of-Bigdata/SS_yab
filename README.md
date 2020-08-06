# SS_Yab

#### Tasks
- [x] Sahamyab Crawler - NSQ Producer
- [x] Tweet Preprocessing - Cassandra DBMS
- [x] Elastic - Kibana dashboard - Redis 
- [ ] Flask dashboard 
- [ ] ML model
- [ ] Clickhouse DBMS - PowerBI visualization

## Prerequisites

```
NSQ
pynsq (pip package)
colorama (pip package)
requests (pip package)
openjdk-8
Cassandra
cassandra-driver (pip package)
hazm (pip package)
nltk (pip package)
elasticsearch (pip package)
redis (pip package)
wordcloudfa (pip package)

flask-login(pip package)
```

## Installing
### - NSQ

1- Download latest NSQ binaries [HERE](https://nsq.io/deployment/installing.html).  
2- Extract the archive, add bin folder to system PATH variable.  
3- Install prerequisties libraries:
```
$ pip install pynsq colorama requests
$ pip install hazm
$ pip install https://github.com/sobhe/hazm/archive/master.zip --upgrade
```
### - Preprocess
1- Install prerequisites libraries:
```
$ pip install hazm (also will install nltk as prerequisite)
$ pip install https://github.com/sobhe/hazm/archive/master.zip --upgrade
```
2- Download and extract nlp prerequisite [resource.zip](https://drive.google.com/file/d/1xf1NdmM_P5_3mt-74ausrst0xKpcD3L3/view?usp=sharing) in project folder.

### - Cassandra
1- Install jdk-8
```
$ sudo apt-get install openjdk-8-jdk
$ export JAVA_HOME=path_to_java_home
```
2- Install [Cassandra](https://cassandra.apache.org/download/):
```
$ echo "deb https://downloads.apache.org/cassandra/debian 311x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
$ curl https://downloads.apache.org/cassandra/KEYS | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install cassandra
```
3- Install Cassandra Python Driver ([cassandra-driver](https://docs.datastax.com/en/developer/python-driver/3.23/installation/)):
```
$ pip install cassandra-driver
```

### - Elasticsearch & Kibana
1- Install [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) & [Kibana](https://www.elastic.co/guide/en/kibana/current/install.html). (We are using 7.8.0)

For Ubuntu, follow these steps:  
- Elasticsearch:
```
$ wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
$ sudo apt-get install apt-transport-https
$ echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
$ sudo apt-get update && sudo apt-get install elasticsearch
```

- Kibana:
```
$ wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
$ sudo apt-get install apt-transport-https
$ echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
$ sudo apt-get update && sudo apt-get install kibana
```

2- Install [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/en/master/api.html)
```
$ python -m pip install elasticsearch
```

### - Redis
1- Install [Redis](https://redis.io/)
```
$ sudo apt update
$ sudo apt install redis-server
```

2- In the config file, change ``supervised no`` to ``supervised systemd``, so it will run with the system start-up.  
In the end, restart the server:
```
$ sudo systemctl restart redis.service
```

3- Install [redis-py](https://redis-py.readthedocs.io/en/stable/) (or [here](https://pypi.org/project/redis/)):
```
$ pip install redis
```

## Usage
1- In one shell, start ``nsqlookupd``:  
```
$ nsqlookupd
```
2- In another shell, start ``nsqd``:
```
$ nsqd --lookupd-tcp-address=127.0.0.1:4160
```
3- In another shell, start ``nsqadmin``:
```
$ nsqadmin --lookupd-http-address=127.0.0.1:4161
```
4- Now run Sahamyab tweet crawler/producer:
```
$ python sahamyab_producer.py
```
5- You can run an example program for consuming tweets:
```
$ python sahamyab_consumer_example.py
```
** To use consumer.py you must first run these:  
Cassandra:
```
$ sudo Cassandra -R
```
Elasticsearch:
```
$ sudo /bin/systemctl daemon-reload
$ sudo /bin/systemctl enable elasticsearch.service
$ sudo systemctl start elasticsearch.service
```
Kibana:
```
$ sudo /bin/systemctl daemon-reload
$ sudo /bin/systemctl enable kibana.service
$ sudo systemctl start kibana.service
```
Also you need to import ```dashboard.ndjson``` into Kibana (Saved objects).

Redis:
If u did that config part, should already be runnig; if not:
```
$ sudo systemctl start redis.service
```

## License

This project is licensed under the GPLv2 - see the [LICENSE.md](LICENSE.md) file for details
