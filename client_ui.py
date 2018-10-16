import base64
import csv
import json
import random
import string
import sys

import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TweakerWidget(QWidget):
    HEADERS = {'Content-type': 'application/json',
               'Accept': 'application/json'}

    def __init__(self):
        super(TweakerWidget, self).__init__()
        self.json_buffer = ''
        self.uri = ''.join(['http://127.0.0.1:8000/tweaker/api/uploads/',
                            ''.join(random.choices(
                                string.ascii_letters + string.digits, k=20)),
                            '.json'])
        self.init_ui()

    def init_ui(self):
        self.setGeometry(0, 0, 1600, 900)
        self.center()
        self.setWindowTitle('Tweaker UI Client')

        # Empty Table
        self.table = QTableWidget(1, 1, self)

        # Import CSV Button
        import_btn = QPushButton('Импорт CSV', self)
        import_btn.resize(import_btn.sizeHint())
        import_btn.clicked.connect(self.import_csv)

        # Upload CSV Button
        self.upload_btn = QPushButton('Загрузка CSV', self)
        self.upload_btn.resize(self.upload_btn.sizeHint())
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_csv)

        # Plot Button
        self.plot_btn = QPushButton('Поехали!', self)
        self.plot_btn.resize(self.plot_btn.sizeHint())
        self.plot_btn.setEnabled(False)
        self.plot_btn.clicked.connect(self.run_query)

        # Upload Status Label
        self.upload_status = QLabel(self)
        self.upload_status.setText('Статус: нет данных')

        # JSON Label
        self.json_status = QLabel(self)
        self.json_status.setText('')
        self.json_status.setAlignment(Qt.AlignCenter)

        # Text Field
        self.query_text = QPlainTextEdit(self)

        # Query Results
        self.result = QTabWidget(self)

        # Grid Layout
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(import_btn, 0, 0)
        self.grid.addWidget(self.upload_btn, 0, 1)
        self.grid.addWidget(self.upload_status, 0, 2)
        self.grid.addWidget(self.table, 1, 0, 5, 3)
        self.grid.addWidget(self.query_text, 4, 3, 2, 4)
        self.grid.addWidget(self.json_status, 5, 7, 1, 2)
        self.grid.addWidget(self.plot_btn, 4, 7, 1, 2)
        self.grid.addWidget(self.result, 0, 3, 4, 6)

        self.show()

    def import_csv(self):
        file_path = QFileDialog.getOpenFileName(caption='Upload CSV',
                                                directory='~',
                                                filter='CSV files (*.csv)')[0]
        if file_path:
            with open(file_path, newline='') as fp:
                dialect = csv.Sniffer().sniff(fp.read(1024))
                fp.seek(0)
                reader = csv.reader(fp, dialect)
                header = next(reader)
                json_buffer = dict(zip(header, [dict() for _ in header]))
                self.table.setColumnCount(len(header))
                for i, label in enumerate(header):
                    self.table.setItem(0, i, QTableWidgetItem(label))
                for i, row in enumerate(reader):
                    self.table.setRowCount(i + 2)
                    for j, val in enumerate(row):
                        json_buffer[header[j]][str(i)] = val
                        self.table.setItem(i + 1, j, QTableWidgetItem(val))
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            self.json_buffer = json.dumps(json_buffer)
            self.upload_btn.setEnabled(True)
            self.upload_status.setText('Статус: данные готовы к загрузке')

    def upload_csv(self):
        try:
            response = requests.post(self.uri,
                                     json=self.json_buffer,
                                     headers=self.HEADERS)
            if response.status_code is 201:
                self.uri = response.json()['uri']
                self.upload_status.setText('Статус: данные успешно загружены')
                self.json_status.setText('Статус: ожидается запрос')
                self.plot_btn.setEnabled(True)
                self.upload_btn.setEnabled(False)
                self.query_text.setPlainText('''{
                "target":"y",
                "groups":{
                    "group1":{"x1": 5,"x3": -2},
                    "group2":{"x5": -3,"x8": 1}
                    }
                }''')
            else:
                self.upload_status.setText(
                    f'Статус: ошибка {response.status_code}')
        except requests.exceptions.ConnectionError:
            self.upload_status.setText('Статус: нет подключения к серверу')

    def run_query(self):
        try:
            query = json.dumps(json.loads(self.query_text.toPlainText()))
            response = requests.get(self.uri,
                                    json=query,
                                    headers=self.HEADERS)
            if response.status_code is 200:
                self.json_status.setText('Статус: запрос успешно обработан')
                self.result.setParent(None)
                self.result, tabs = QTabWidget(self), []
                self.grid.addWidget(self.result, 0, 3, 4, 6)
                for i, cmb in enumerate(response.json()['predictions']):
                    tabs.append(QWidget(self.result))
                    self.result.addTab(tabs[-1], str(i + 1))
                    pixmap = QPixmap()
                    pixmap.loadFromData(base64.b64decode(cmb['plot']))
                    plot = QLabel(tabs[-1])
                    plot.setPixmap(pixmap)
                    plot.setAlignment(Qt.AlignCenter)
                    table = QTableWidget(1, len(cmb['pred']), self)
                    for j, y in enumerate(cmb['pred']):
                        table.setItem(0, j, QTableWidgetItem(y))
                    table.setSizeAdjustPolicy(
                        QAbstractScrollArea.AdjustToContents)
                    table.resizeRowsToContents()
                    table.resizeColumnsToContents()
                    layout = QGridLayout()
                    layout.addWidget(plot, 0, 0)
                    layout.addWidget(table, 1, 0)
                    tabs[-1].setLayout(layout)
                    self.result.setTabText(i, str(i + 1))
            else:
                self.json_status.setText(
                    f'Статус: ошибка {response.status_code}')
        except ValueError:
            self.json_status.setText('Статус: не соблюден синтаксис json')
        except requests.exceptions.ConnectionError:
            self.upload_status.setText('Статус: нет подключения к серверу')

    def center(self):
        qr = self.frameGeometry()
        qr.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TweakerWidget()
    app.exec_()
