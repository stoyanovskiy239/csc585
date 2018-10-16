import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from itertools import chain, combinations
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')


class DataTweaker:
    """Класс-обертка для модели и данных"""

    def __init__(self, model, dataframe, target_label):
        self.model = model
        self.X = dataframe.drop(target_label, axis=1)
        self.y = dataframe[target_label].mean()
        self.lbl = target_label
        self.groups = []

    # генератор сочетаний
    @property
    def combinations(self):
        gr_rng = range(len(self.groups))
        return chain.from_iterable(
            combinations(gr_rng, k + 1)
            for k in gr_rng
        )

    # добавить группу параметров
    def add_gr(self, group):
        self.groups.append(group)

    # удалить группу по номеру
    def remove_gr(self, group_id):
        del self.groups[group_id]

    # очистить список групп
    def clear_gr(self):
        self.groups = []

    # вывести группы
    def show_gr(self):
        for i, gr in enumerate(self.groups):
            print(f'#{i}:', end=' ')
            items = []
            for feat, delta in gr.items():
                sgn = '+' if delta > 0 else ''
                items.append(f'{feat}({sgn}{delta})')
            print(', '.join(items))
        print()

    # сделать 10 "шагов" группой параметров
    def tweak(self, group_id_list):
        y_pred = [0] * 11
        y_pred[0] = self.y
        X = self.X.copy()
        for i in range(10):
            for gr_id in group_id_list:
                for feat, delta in self.groups[gr_id].items():
                    X[feat] += delta
            y_pred[i + 1] = model.predict(X).mean()
        return y_pred

    # "пошагать" всеми сочетаниями групп
    # и вывести результат, можно с графиками
    def tweak_all(self, plot=False):
        for cmb in self.combinations:
            title = ', '.join([f'#{i}' for i in cmb])
            title = ' '.join(['groups:', title])
            pred = self.tweak(cmb)
            print(title)
            print(*pred, sep='\n', end='\n\n')
            if plot:
                plt.plot(pred, marker='o')
                plt.title(title)
                plt.xticks(range(11))
                plt.xlabel('steps')
                plt.ylabel(self.lbl)
                plt.show()


# генерируем данные
# X - случайная матрица чисел от 0 до 99
# y - 0 если сумма в строке меньше 500, 1 если больше
X_train = np.random.randint(0, 100, size=(70000, 10))
y_train = np.array(
    [int(row.sum() > 500) for row in X_train]
)
# обучаем модель
model = DecisionTreeClassifier(
    min_samples_leaf=100).fit(X_train, y_train)

# генерируем новые данные по тому же принципу
data = pd.DataFrame(
    np.random.randint(0, 100, size=(30000, 10)),
    columns=[f'x{i+1}' for i in range(10)]
)
data['y'] = np.array(
    [int(row.sum() > 500) for row in data.values]
)

# оборачиваем все в наш класс
dt = DataTweaker(model, data, 'y')
# группы в виде словарей {имя параметра: шаг изменения}
dt.add_gr({'x1': 5})
dt.add_gr({'x3': -10, 'x7': -2})
dt.add_gr({'x5': 1, 'x9': -3})
# выводим группы
dt.show_gr()

# сбсно, главный экшн
dt.tweak_all(
    # plot=True
)
