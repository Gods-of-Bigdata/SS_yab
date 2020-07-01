# Sahamyab

#### Tasks
- [x] Sahamyab Crawler - NSQ Producer
- [ ] Tweet Preprocessing - Kibana dashboard - Flask dashboard 
- [ ] Cassandra DBMS - ML model
- [ ] Clickhouse DBMS - PowerBI visualization

### Prerequisites

```
NSQ
pynsq (pip package)
colorama (pip package)
requests (pip package)
```

### Installing

1- Download latest NSQ binaries [HERE](https://nsq.io/deployment/installing.html).  
2- Extract the archive, add bin folder to system PATH variable.
3- In one shell, start ``nsqlookupd``:
```
$ nsqlookupd
```
4- In another shell, start ``nsqd``:
```
$ nsqd --lookupd-tcp-address=127.0.0.1:4160
```
5- In another shell, start ``nsqadmin``:
```
$ nsqadmin --lookupd-http-address=127.0.0.1:4161
```
6- Install prerequisties libraries:
```
$ pip install pynsq colorama requests
```
7- Now run Sahamyab tweet crawler/producer:
```
$ python sahamyab_producer.py
```
8- You can run an example program for consuming tweets:
```
$ python sahamyab_consumer_example.py
```

## License

This project is licensed under the GPLv2 - see the [LICENSE.md](LICENSE.md) file for details
