import base64
from io import BytesIO
from itertools import chain, combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

_X = np.random.randint(0, 100, size=(70000, 10))
_y = np.array([int(row.sum() > 500) for row in _X])
MODEL = DecisionTreeClassifier(min_samples_leaf=100).fit(_X, _y)


def tweak(json_data, target, groups):
    X = pd.read_json(json_data)
    y = X[target].mean()
    X.drop(target, axis=1, inplace=True)

    predictions = []
    for group_cmb in chain.from_iterable(
            combinations(groups.keys(), k + 1) for k in range(len(groups))
    ):
        X_copy = X.copy()
        pred = [y] + [0] * 10
        for i in range(10):
            for gr in group_cmb:
                for feat, step in groups[gr].items():
                    X_copy[feat] += step
            pred[i + 1] = MODEL.predict(X_copy).mean()
        plt.rcParams["figure.figsize"] = [10, 5]
        plt.plot(pred, marker='o')
        plt.title(' + '.join(group_cmb))
        plt.xticks(range(11))
        plt.xlabel('steps')
        plt.ylabel('target')
        plt.grid()
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.clf()
        predictions.append({
            'groups': list(group_cmb),
            'pred': pred,
            'plot': str(base64.b64encode(img.getvalue()).decode())
        })
    return predictions
