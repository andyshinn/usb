from flask import Flask, escape, request, make_response, send_file
from pathlib import Path
import random

from usb.tasks import extract_thumbnail_id
from usb.search import Appsearch

app = Flask(__name__)

@app.route('/image/<id>.png')
def get_image(id):
    path = Path(f'/thumbnails/{id}.png')
    if path.is_file():
        return send_file(path)
    else:
        task = extract_thumbnail_id.delay(id)
        resp = make_response(f'{escape(id)} is being processed as task {escape(task)}', 202)
        resp.headers['Retry-After'] = 10
        return resp


@app.route('/search/<query>')
def image_search(query):
    search = Appsearch()
    results = search.query(escape(query))

    if results['results']:
        if request.args.get('rand', None):
            result = random.choice(results['results'])
        else:
            result = results['results'][0]

        id = result['id']['raw']
    else:
        return "no results found", 404

    path = Path(f'/thumbnails/{id}.png')

    if path.is_file():
        return send_file(path)
    else:
        task = extract_thumbnail_id.delay(id)
        resp = make_response(f'generating {escape(id)} for query {escape(query)}\nrefresh page in a moment', 202)
        resp.headers['Retry-After'] = 10
        return resp
