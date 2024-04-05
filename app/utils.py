import hashlib
import random
import string

from . import redis

def generate_short_link(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    hex_dig = hash_object.hexdigest()

    short_link = hex_dig[:10]
    while short_link in redis.scan_iter():
        url = redis.get(short_link).decode('utf-8')
        if url == long_url:
            return short_link
        short_link = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    return short_link
