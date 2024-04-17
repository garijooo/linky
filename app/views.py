from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    jsonify,
)
import re

from .utils import generate_short_link
from . import redis_store

bp = Blueprint("api", __name__, template_folder="templates")


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/shorten-link", methods = ["POST"])
def shorten_link():
    full_link = request.json.get("fullLink", None)
    if not full_link:
        return jsonify({"error": "The link was not provided"}), 400
    elif len(full_link.split(".")) < 2:
        return jsonify({"error": "Please provide a valid link"}), 400
    elif re.match(r'^(?!https?://)', full_link) is not None:
        full_link = 'http://' + full_link
    short_link = generate_short_link(full_link)
    redis_store.set(short_link, full_link)
    return jsonify({"short_link": "http://localhost:5000/" + short_link})


@bp.route('/<short_link>')
def redirect_to_url(short_link):
    url = redis_store.get(short_link)
    if not url:
        return redirect('/', 307)
    return redirect(url.decode('utf-8'), 302)
