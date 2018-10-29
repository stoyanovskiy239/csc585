import json
import os
import re

from flask import Flask, abort, request, make_response, jsonify, url_for

from legacyCode.legacyML import tweak

UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

VALID_FILENAME = re.compile('\S+\.json')

app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({'error': 'conflict'}), 409)


@app.route('/tweaker/api/uploads/<filename>', methods=['POST'])
def upload_data(filename):
    if not (request.json and VALID_FILENAME.fullmatch(filename)):
        abort(400)
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        abort(409)
    with open(file_path, 'w') as fp:
        json.dump(request.json, fp)
    return jsonify({'uri': url_for('get_predictions',
                                   filename=filename,
                                   _external=True)
                    }), 201


@app.route('/tweaker/api/uploads/<filename>', methods=['GET'])
def get_predictions(filename):
    if not (request.json and VALID_FILENAME.fullmatch(filename)):
        abort(400)
    file_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(file_path) as fp:
            data = json.load(fp)
    except OSError:
        abort(404)
    query = json.loads(request.json)
    return jsonify({'predictions': tweak(data,
                                         query['target'],
                                         query['groups'])
                    }), 200


if __name__ == '__main__':
    app.run(port=8000, debug=True)
