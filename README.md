# SS_Yab

#### Tasks
- [x] Sahamyab Crawler - NSQ Producer
- [x] Tweet Preprocessing - Cassandra DBMS
- [ ] Kibana dashboard - Flask dashboard 
- [ ] ML model
- [ ] Clickhouse DBMS - PowerBI visualization

### Prerequisites

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

### Installing

1- Download latest NSQ binaries [HERE](https://nsq.io/deployment/installing.html).  
2- Extract the archive, add bin folder to system PATH variable.  
3- Install prerequisties libraries:
```
$ pip install pynsq colorama requests
$ pip install hazm
$ pip install https://github.com/sobhe/hazm/archive/master.zip --upgrade
```


### Usage
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

## License

This project is licensed under the GPLv2 - see the [LICENSE.md](LICENSE.md) file for details
