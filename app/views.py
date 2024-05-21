from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    jsonify,
)
import re

from .utils import add_short_link, get_full_link, user_short_link_exists
from . import redis_store

bp = Blueprint("api", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/links/<user_id>")
def links(user_id):
    user_cookie_id = request.cookies.get("userId")
    user_key = f"user:{user_id}"
    user_urls = redis_store.lrange(user_key, 0, -1)
    urls = [{
        "short_link": uu.decode("utf-8"),
        "full_link": redis_store.get(uu.decode("utf-8")).decode("utf-8"),
    } for uu in user_urls if redis_store.get(uu.decode("utf-8"))]
    return render_template(
        "links.html",
        urls=urls,
        user_id=user_id,
        is_mine=user_cookie_id == user_id,
    )


@bp.route("/shorten-link", methods = ["POST"])
def shorten_link():
    full_link = request.json.get("fullLink", None)
    user_cookie_id = request.cookies.get("userId")
    if not full_link:
        return jsonify({"error": "The link was not provided"}), 400
    elif len(full_link.split(".")) < 2:
        return jsonify({"error": "Please provide a valid link"}), 400
    elif re.match(r'^(?!https?://)', full_link) is not None:
        full_link = 'http://' + full_link
    short_link, user_id = add_short_link(full_link=full_link, user_id=user_cookie_id)
    return jsonify({"short_link": "http://localhost:5000/" + short_link, "user_id": user_id})


@bp.route("/link/<short_link>", methods=["DELETE"])
def delete_link(short_link):
    success = False
    user_cookie_id = request.cookies.get("userId")
    if user_cookie_id is not None:
        if user_short_link_exists(short_link, user_cookie_id):
            user_key = f"user:{user_cookie_id}"
            redis_store.lrem(user_key, 1, short_link)
            success = True
    if success is True:
        redis_store.delete(short_link)
        return jsonify({"success": True})
    elif not user_cookie_id:
        return jsonify({"error": "Authorization error"}), 401
    return jsonify({"error": "Something went wrong"}), 400


@bp.route('/<short_link>')
def redirect_to_url(short_link):
    url = get_full_link(short_link=short_link)
    if url is None:
        return redirect('/', 307)
    return redirect(url, 302)
