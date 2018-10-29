import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def make_model(model_specs):
    if model_specs['mode'] is 'C':
        model = RandomForestClassifier()
    else:
        model = RandomForestRegressor()
    data = pd.DataFrame.from_dict(model_specs['data'], orient='columns')
    X = data.drop(model_specs['target'], axis=1)
    y = data[model_specs['target']]
    model.fit(X, y)
    return model, list(X)


def rank_features(model, ft_names):
    ft_importances = model.feature_importances_
    indices = np.argsort(ft_importances)[::-1]
    ft_ranking = [(ft_names[indices[i]], ft_importances[indices[i]])
                  for i in range(len(ft_names))]
    return ft_ranking
