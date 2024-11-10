"""Redis data"""
import redis

r = redis.StrictRedis(host='redis-stack', port=6379, db=0, decode_responses=True)
