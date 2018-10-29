import json
import os
import re
import uuid
import pickle
from flask import Flask, abort, request, make_response, jsonify

from legacyCode.legacyML import tweak
from tweakerAPI.coreML import make_model, rank_features

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


@app.route('/tweaker/v1/uploads', methods=['POST'])
def upload_data():
    if not request.json:
        abort(400)
    request_json = json.loads(request.json)
    model, feature_names = make_model(request_json)
    feature_ranking = rank_features(model, feature_names)
    file_id = uuid.uuid4()
    file_path = os.path.join(UPLOAD_DIR, str(file_id))
    with open(file_path + '.json', 'w') as file:
        json.dump(request_json['data'], file)
    with open(file_path + '.mdl', 'wb') as file:
        pickle.dump(model, file)
    return jsonify({'uuid': file_id,
                    'featRanking': feature_ranking}), 201


@app.route('/tweaker/v1/uploads/<filename>', methods=['GET'])
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
