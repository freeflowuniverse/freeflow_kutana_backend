from redis import StrictRedis
from flask import g


def connect_redis():
    try:
        if 'redis' not in g:
            g.redis = StrictRedis(host='ffc_backend_redis', port=6379, decode_responses=True)

        return g.redis
    except Exception as ex:
        print('Failed to connect redis: {}'.format(ex))
