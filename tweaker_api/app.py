import os
import re
import json
from flask import Flask, abort, request, make_response, jsonify, url_for

from tweaker_api.core.tweak_ml_core import tweak

UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# для поверки запросов
VALID_FILENAME = re.compile('\S+\.json')

app = Flask(__name__)


# обработчики ошибок
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(409)
def conflict(error):
    return make_response(jsonify({'error': 'conflict'}), 409)


# POST метод для загрузки csv (перекинутых в json)
@app.route('/tweaker/api/uploads/<filename>', methods=['POST'])
def upload_data(filename):
    # проверяем запрос
    # если он не по форме, то возвращаем 400 (bad request)
    if not (request.json and VALID_FILENAME.fullmatch(filename)):
        abort(400)
    file_path = os.path.join(UPLOAD_DIR, filename)
    # если уже есть файл с таким именем, возвращаем 409 (conflict)
    if os.path.exists(file_path):
        abort(409)
    # сохраняем json
    with open(file_path, 'w') as fp:
        json.dump(request.json, fp)
    # возвращаем uri загруженного файла и 201 (created)
    return jsonify({'uri': url_for('get_predictions',
                                   filename=filename,
                                   _external=True)
                    }), 201


# GET метод для получения результатов "шагания" группами
@app.route('/tweaker/api/uploads/<filename>', methods=['GET'])
def get_predictions(filename):
    # проверяем запрос
    # если он не по форме, то возвращаем 400 (bad request)
    if not (request.json and VALID_FILENAME.fullmatch(filename)):
        abort(400)
    file_path = os.path.join(UPLOAD_DIR, filename)
    # пытаемся открыть интересующий пользователя файл
    # если не находим, то возвращаем 404 (not found)
    try:
        with open(file_path) as fp:
            data = json.load(fp)
    except OSError:
        abort(404)
    # превращаем json-строку с деталями запроса в объект
    query = json.loads(request.json)
    # возвращаем результат работы функции tweak,
    # которой мы скормили данные из файла и
    # детали запроса про таргет и группы
    # и 200 (ok)
    return jsonify({'predictions': tweak(data,
                                         query['target'],
                                         query['groups'])
                    }), 200


if __name__ == '__main__':
    app.run(port=8000, debug=True)
