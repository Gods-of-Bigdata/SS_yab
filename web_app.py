from flask import Flask, render_template, request
from cassandra.cluster import Cluster
from redis.client import Redis
from elasticsearch import Elasticsearch
from db_utils import CassandraApi,redisApi,elasticQuery

redis_client = Redis("localhost", port=6379)
redis_api = redisApi(redis_client)
cassandra_api = CassandraApi('sahamyab')
es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])


#%%
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
@app.route('/cassandra', methods=['GET', 'POST'])
def cassandraRoutine():
        data = request.form.to_dict()
        if request.method == 'POST':
            result_set = cassandra_api.cassandraQuery(data)
            output = elasticQuery(es_client,result_set)
            return render_template("cassandra.html",db_result=output)
        else:
            return render_template("cassandra.html")

@app.route('/redis', methods=['GET', 'POST'])
def redisRoutine():
        data = request.form.to_dict()
        lists = redis_api.redis_list()
        if request.method == 'POST':
            counts = redis_api.redis_query(data)  
            return render_template("redis.html", redis_lists=lists, redis_counts=counts)
        else:
            return render_template("redis.html", redis_lists=lists)

    


if __name__ == '__main__':
    app.run()
