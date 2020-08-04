import sys
import os.path as osp
import json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLayout, QListWidgetItem
import designs.analyze as design
import qdarkstyle
from collections import OrderedDict


class PomodoroGUI(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, path_to_file):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.path_to_file = path_to_file
        self.load_projects()

        #self.listWidget.itemSelectionChanged.connect(self.populate_tasks)
        self.populate_projects()
        self.listWidget.clicked.connect(self.populate_tasks)
        self.listWidget_2.clicked.connect(self.populate_poms)
        self.listWidget_3.clicked.connect(self.populate_interrupts)

        self.populate_dates_ro()
        self.listWidget_5.clicked.connect(self.populate_projects_ro)
        self.listWidget_6.clicked.connect(self.populate_tasks_ro)
        self.listWidget_7.clicked.connect(self.populate_pomodoros_ro)
        self.listWidget_8.clicked.connect(self.populate_interrupts_ro)

# organize by project:

    def populate_projects(self):
        for k in self.data.keys():
            nr = self.data[k]['_nr_poms_']
            QListWidgetItem('{} | [{}]'.format(k, nr), self.listWidget)

    def populate_tasks(self):
        self.listWidget_2.clear()
        self.listWidget_3.clear()
        self.listWidget_4.clear()
        k = self.listWidget.currentItem().text().split('|')[0][:-1]
        for l in self.data[k].keys():
            if l == '_nr_poms_':
                continue
            nr = len(self.data[k][l].keys())
            QListWidgetItem('{} | [{}]'.format(l, nr), self.listWidget_2)

    def populate_poms(self):
        self.listWidget_3.clear()
        self.listWidget_4.clear()
        k = self.listWidget.currentItem().text().split('|')[0][:-1]
        l = self.listWidget_2.currentItem().text().split('|')[0][:-1]
        for m in self.data[k][l].keys():
            nr = len(self.data[k][l][m])
            if nr == 1 and self.data[k][l][m][0] == '':
                # if no interrupts, only item is empty string
                nr = 0
            QListWidgetItem('{} | [{}]'.format(m, nr), self.listWidget_3)

    def populate_interrupts(self):
        self.listWidget_4.clear()
        k = self.listWidget.currentItem().text().split('|')[0][:-1]
        l = self.listWidget_2.currentItem().text().split('|')[0][:-1]
        m = self.listWidget_3.currentItem().text().split('|')[0][:-1]
        for n in self.data[k][l][m]:
            QListWidgetItem(n, self.listWidget_4)

# organize by date:

    def populate_dates_ro(self):

        for k in self.data_reordered.keys():
            nr = self.data_reordered[k]['_nr_poms_']
            QListWidgetItem('{} | [{}]'.format(k, nr), self.listWidget_5)

    def populate_projects_ro(self):
        self.listWidget_6.clear()
        self.listWidget_7.clear()
        self.listWidget_8.clear()
        self.listWidget_9.clear()
        k = self.listWidget_5.currentItem().text().split('|')[0][:-1]
        for l in self.data_reordered[k].keys():
            if l == '_nr_poms_':
                continue
            nr = self.data_reordered[k][l]['_nr_poms_']
            QListWidgetItem('{} | [{}]'.format(l, nr), self.listWidget_6)

    def populate_tasks_ro(self):
        self.listWidget_7.clear()
        self.listWidget_8.clear()
        self.listWidget_9.clear()
        k = self.listWidget_5.currentItem().text().split('|')[0][:-1]
        l = self.listWidget_6.currentItem().text().split('|')[0][:-1]
        for m in self.data_reordered[k][l].keys():
            if m == '_nr_poms_':
                continue
            nr = len(self.data_reordered[k][l][m])
            QListWidgetItem('{} | [{}]'.format(m, nr), self.listWidget_7)

    def populate_pomodoros_ro(self):
        self.listWidget_8.clear()
        self.listWidget_9.clear()
        k = self.listWidget_5.currentItem().text().split('|')[0][:-1]
        l = self.listWidget_6.currentItem().text().split('|')[0][:-1]
        m = self.listWidget_7.currentItem().text().split('|')[0][:-1]
        for n in self.data_reordered[k][l][m].keys():
            nr = len(self.data_reordered[k][l][m][n])
            if nr == 1 and self.data_reordered[k][l][m][n][0] == '':
                # if no interrupts, only item is empty string
                nr = 0

            QListWidgetItem('{} | [{}]'.format(n, nr), self.listWidget_8)

    def populate_interrupts_ro(self):
        self.listWidget_9.clear()
        k = self.listWidget_5.currentItem().text().split('|')[0][:-1]
        l = self.listWidget_6.currentItem().text().split('|')[0][:-1]
        m = self.listWidget_7.currentItem().text().split('|')[0][:-1]
        n = self.listWidget_8.currentItem().text().split('|')[0][:-1]
        for o in self.data_reordered[k][l][m][n]:
            QListWidgetItem(o, self.listWidget_9)

    def load_projects(self):
        with open(self.path_to_file, 'r') as f:
            d = json.load(f)
            self.data = self.order_dict(d)
            self.data_reordered = self.reorganize_dict(d)

    @staticmethod
    def order_dict(d):
        sd = []
        for a in d:
            for b in d[a]:
                for c in d[a][b]:
                    sd.append([a, b, c])
        # sort by date of last pomodoro
        sd.sort(key=lambda x: x[2], reverse=True)

        od = OrderedDict()

        for a, b, c in sd:
            try:
                od[a]
            except KeyError:
                od[a] = OrderedDict()
            try:
                od[a]['_nr_poms_']
            except KeyError:
                od[a]['_nr_poms_'] = 0
            try:
                od[a][b]
            except KeyError:
                od[a][b] = OrderedDict()
            od[a]['_nr_poms_'] += 1
            od[a][b][c] = d[a][b][c]

        return od

    @staticmethod
    def reorganize_dict(d):
        """ uses date as first key"""
        sd = []
        for a in d:
            for b in d[a]:
                for c in d[a][b]:
                    sd.append([a, b, c])
        sd.sort(key=lambda x: x[2], reverse=True)

        od = OrderedDict()

        for a, b, c in sd:
            datekey = c[:8]
            try:
                od[datekey]
            except KeyError:
                od[datekey] = OrderedDict()
            try:
                od[datekey]['_nr_poms_']
            except KeyError:
                od[datekey]['_nr_poms_'] = 0
            try:
                od[datekey][a]
            except KeyError:
                od[datekey][a] = OrderedDict()
            try:
                od[datekey][a]['_nr_poms_']
            except KeyError:
                od[datekey][a]['_nr_poms_'] = 0
            try:
                od[datekey][a][b]
            except KeyError:
                od[datekey][a][b] = OrderedDict()
            od[datekey]['_nr_poms_'] += 1
            od[datekey][a]['_nr_poms_'] += 1
            od[datekey][a][b][c[8:]] = d[a][b][c]  # only time for c

        return od

    def save(self):
        with open(self.path_to_file, 'w') as f:
            f.write(json.dumps(self.data, indent=4))


def start_pomodoro(path_to_file):
    app = QtWidgets.QApplication(sys.argv)

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = PomodoroGUI(path_to_file)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    this_path_to_file = 'pomodoros.json'
    start_pomodoro(this_path_to_file)
