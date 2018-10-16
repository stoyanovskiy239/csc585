import requests
import pandas as pd
import numpy as np
import json
import os

API_URL = 'http://127.0.0.1:8000/tweaker/api'

# генерируем данные для теста
data = pd.DataFrame(np.random.randint(0, 100, size=(30000, 10)),
                    columns=[f'x{i+1}' for i in range(10)])
data['y'] = np.array([int(row.sum() > 500) for row in data.values])
# в json
data = data.to_json()

# составляем запрос
uri = os.path.join(API_URL, 'uploads', 'test.json')
# отправляем на сервер
response = requests.post(uri, json=data)
# выводим ответ
if response.status_code is 201:
    uri = response.json()['uri']
    print('successfully uploaded')
    print(uri)
else:
    print('code: ', response.status_code)
    quit(0)

# составляем запрос с таргетом и группами
query = json.dumps(
    {
        "target": "y",
        "groups": {
            "group1": {
                "x1": 5,
                "x3": -2
            },
            "group2": {
                "x5": -3,
                "x8": 1}
        }
    }
)

# отправляем на сервер
response = requests.get(uri, json=query)
# выводим ответ
if response.status_code is 200:
    print('predictions successfully acquired')
    print(response.json())
else:
    print('code: ', response.status_code)
