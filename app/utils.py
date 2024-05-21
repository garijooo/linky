from uuid import uuid4
import hashlib
import random
import string

from . import redis_store


def user_short_link_exists(short_link: str, user_id: str) -> bool:
    user_key = f"user:{user_id}"
    user_urls = [v.decode('utf-8') for v in redis_store.lrange(user_key, 0, -1)]
    return short_link in user_urls


def generate_short_link(full_link: str, user_id: str) -> str:
    if not full_link:
        raise ValueError("Provide long full link")

    hash_object = hashlib.sha256(full_link.encode())
    hex_dig = hash_object.hexdigest()
    short_link = hex_dig[:10]
    exists = user_short_link_exists(short_link, user_id)

    while redis_store.exists(short_link) or exists:
        stored_url = redis_store.get(short_link)
        if (
            stored_url is not None
            and stored_url.decode("utf-8") == full_link
            and exists is True
        ):
            return short_link
        short_link = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        exists = user_short_link_exists(short_link, user_id)
    return short_link


def get_full_link(short_link) -> str:
    full_url = redis_store.get(short_link)
    return full_url.decode("utf-8") if full_url else None


def add_short_link(full_link: str, user_id = None) -> tuple[str, str]:
    if user_id is None:
        user_id = uuid4()
    short_link = generate_short_link(full_link, user_id)
    if not redis_store.exists(short_link):
        user_key = f"user:{user_id}"
        redis_store.rpush(user_key, short_link)
        redis_store.set(short_link, full_link)
    return short_link, user_id


def remove_short_link(short_link: str, user_id: str = None) -> None:
    if user_id is not None:
        if user_short_link_exists(short_link, user_id):
            user_key = f"user:{user_id}"
            redis_store.lrem(user_key, 1, short_link)
    redis_store.delete(short_link)
