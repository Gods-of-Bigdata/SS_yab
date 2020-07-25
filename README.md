# SS_Yab

#### Tasks
- [x] Sahamyab Crawler - NSQ Producer
- [x] Tweet Preprocessing - Cassandra DBMS
- [ ] Kibana dashboard - Flask dashboard 
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
** for use cassandra_consumer.py you must first run Cassandra:
```
$ sudo Cassandra -R
```

## License

This project is licensed under the GPLv2 - see the [LICENSE.md](LICENSE.md) file for details
