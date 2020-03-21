from flask import Flask, escape, request, make_response, send_file
from pathlib import Path

from usb.tasks import extract_thumbnail_id
from usb.search import Appsearch

app = Flask(__name__)


@app.route("/image/<show>/<id>.png")
def get_image(show, id):
    engine = show.lower()
    path = Path(f"/thumbnails/{id}.png")

    if path.is_file():
        return send_file(path)
    else:
        task = extract_thumbnail_id.delay(engine, id)
        resp = make_response(
            f"{escape(id)} is being processed as task {escape(task)}", 202
        )
        resp.headers["Retry-After"] = 10
        return resp


@app.route("/search/<show>/<query>")
def image_search(show, query):
    search = Appsearch()
    engine = show.lower()

    random = bool(request.args.get("random", False))
    result = search.get(engine, escape(query), random)

    if result:
        id = result["id"]["raw"]
    else:
        return "no result found", 404

    path = Path(f"/thumbnails/{id}.png")

    if not path.is_file():
        task = extract_thumbnail_id.delay(engine, id)
        path = task.get(timeout=10)
        path = Path(path)

    return send_file(path)
