from decouple import config
import redis
host=config('REDIS_HOST')
port=config('REDIS_PORT')
db=config('REDIS_DB')
print(redis.Redis(host=host,port=port,db=db).set("slom","qanday"))