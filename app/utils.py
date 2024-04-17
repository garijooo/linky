import hashlib
import random
import string

from . import redis_store

def generate_short_link(full_link):
    if not full_link:
        raise ValueError("Provide long full link")

    hash_object = hashlib.sha256(full_link.encode())
    hex_dig = hash_object.hexdigest()
    short_link = hex_dig[:10]

    keys = [k.decode('utf-8') for k in redis_store.scan_iter()]
    while short_link in keys:
        url = redis_store.get(short_link)
        if url and url.decode("utf-8") == full_link:
            return short_link
        short_link = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    return short_link
