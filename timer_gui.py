import sys
import os.path as osp
import json
import subprocess
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import QTimer
import apps.pomodoro.designs.pomodoro as design
import datetime
import ctypes
import qdarkstyle
from collections import OrderedDict


class PomodoroGUI(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, path_to_file):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.btn_go.clicked.connect(self.pom)
        self.btn_add_project.clicked.connect(self.add_project)
        self.btn_add_task.clicked.connect(self.add_task)
        self.cb_project.currentTextChanged.connect(self.populate_combo_box_tasks)

        self.secs_elapsed = 0
        self.pb_remaining.setValue(0)
        self.data = None
        self.task = ''
        self.nr_poms = 0
        self.project = ''
        self.do_this = None
        self.ni = 0
        self.timer = None

        self.path_to_file = path_to_file
        self.load_projects()
        self.populate_combo_box_projects()
        self.populate_combo_box_tasks()

        self.groupBox_2.hide()

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.layout().setSizeConstraint(QLayout.SetFixedSize)

    def load_projects(self):
        if not osp.exists(self.path_to_file):
            self.data = OrderedDict()
        else:
            with open(self.path_to_file, 'r') as f:
                try:
                    self.data = self.order_dict(json.load(f))
                except Exception as e:
                    self.data = OrderedDict

    @staticmethod
    def order_dict(d):
        sd = []
        for a in d:
            for b in d[a]:
                for c in d[a][b]:
                    print(a, b, c)
                    sd.append([a, b, c])
        sd.sort(key=lambda x: x[2], reverse=True)

        od = OrderedDict()

        for a, b, c in sd:
            try:
                od[a]
            except KeyError:
                od[a] = OrderedDict()
            try:
                od[a][b]
            except KeyError:
                od[a][b] = OrderedDict()
            od[a][b][c] = d[a][b][c]

        return od

    def save(self):
        with open(self.path_to_file, 'w') as f:
            f.write(json.dumps(self.data, indent=4))

    def add_project(self):
        new_project = self.le_enter_project.text()
        if new_project not in self.data.keys():
            self.data[self.le_enter_project.text()] = {}
            self.save()
            self.populate_combo_box_projects()
            self.cb_project_2.setCurrentText(new_project)

    def add_task(self):
        new_task = self.le_enter_task_2.text()
        project = self.cb_project_2.currentText()
        if new_task not in self.data[self.cb_project_2.currentText()].keys():
            self.data[project][new_task] = {}
            self.save()
            self.populate_combo_box_tasks()
            self.cb_project.setCurrentText(project)
            self.cb_task.setCurrentText(new_task)

    def populate_combo_box_projects(self):
        self.cb_project.clear()
        self.cb_project.addItems(self.data.keys())
        self.cb_project_2.clear()
        self.cb_project_2.addItems(self.data.keys())

    def populate_combo_box_tasks(self):
        try:
            self.cb_task.clear()
            self.cb_task.addItems(self.data[self.cb_project.currentText()].keys())
        except KeyError:
            pass

    def pom(self):
        self.task, self.nr_poms = self.cb_task.currentText(), self.sb_number_of_poms.value()
        self.project = self.cb_project.currentText()
        self.groupBox_2.setTitle(self.project + ' | ' + self.task + ' | ' + '0/{}'.format(self.nr_poms))

        poms_before_big_pause = 4

        work_minutes = ['work', 24]
        pause_minutes = ['pause', 4]
        long_pause_minutes = ['long pause', 14]

        do_this = []
        for i in range(1, self.nr_poms + 1):
            do_this.append(work_minutes)
            if i % poms_before_big_pause == 0:
                do_this.append(long_pause_minutes)
            else:
                do_this.append(pause_minutes)

        # skip last break:
        do_this = do_this[:-1]

        self.do_this = do_this
        self.ni = 0

        self.secs_elapsed = 0

        # hide the Start and new groupBox. show the running groupbox:
        self.groupBox.hide()
        self.groupBox_3.hide()
        self.groupBox_2.show()

        # update clock every 1 s
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)

    def showTime(self):
        self.lbl_status.setText(self.do_this[self.ni][0])
        self.pb_remaining.setValue(100 * (self.secs_elapsed + 1) / ((self.do_this[self.ni][1] + 1) * 60 ))

        self.setWindowTitle('{} | {} | {}/{} | {}: {:02d}:{:02d}'.format(
            self.project,
            self.task,
            int((self.ni / 2) + 1),
            self.nr_poms,
            self.do_this[self.ni][0],
            self.do_this[self.ni][1] - int(self.secs_elapsed / 60),
            59 - (self.secs_elapsed % 60)
        ))

        if self.secs_elapsed + 1 >= (self.do_this[self.ni][1] + 1) * 60:
            self.do_kill_timer()
        else:
            self.secs_elapsed += 1

    def do_kill_timer(self):
        subprocess.call(["ffplay", "-nodisp", "-autoexit", 'whistle.mp3'])
        text = "You finished the item {} of the task {}. ".format(self.do_this[self.ni][0], self.task)
        self.groupBox_2.setTitle('{} | {} | {}/{}'.format(
            self.project,
            self.task,
            int((self.ni / 2) + 1),
            self.nr_poms)
        )

        if self.do_this[self.ni][0] == 'work':
            n = datetime.datetime.now()
            finish_time = '{:04d}{:02d}{:02d}{:02d}{:02d}'.format(n.year, n.month, n.day, n.hour, n.minute)
            interrruptions = [i.strip() for i in self.le_interruption.text().split(',')] \
                if ',' in self.le_interruption.text() else [self.le_interruption.text()]
            self.le_interruption.setText('')
            self.data[self.project][self.task][finish_time] = interrruptions
            self.save()

        ctypes.windll.user32.MessageBoxW(0, text, "Pomodoro Message", 1)
        self.timer.stop()
        self.secs_elapsed = 0
        self.ni += 1
        if self.ni < len(self.do_this):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.showTime)
            self.timer.start(1000)
        else:
            self.groupBox.show()
            self.groupBox_3.show()
            self.groupBox_2.hide()
            text = "You finished the task {}. ".format(self.task)
            ctypes.windll.user32.MessageBoxW(0, text, "Pomodoro Message", 1)


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
