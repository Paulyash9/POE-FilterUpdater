import sys
import os.path as osp
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GUI import *
import tiers as t
import shutil
from Parsedata import Getdata


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, open_file='', save_file='', all_strings=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.SelectAllBtn.clicked.connect(self.SelectAllBtn_clicked)
        self.ui.RemoveAllBtn.clicked.connect(self.RemoveAllBtn_clicked)
        self.ui.OpenFileBtn.clicked.connect(self.OpenFileBtn_clicked)
        self.ui.SaveBtn.clicked.connect(self.SaveBtn_clicked)
        self.ui.SortBtn.clicked.connect(self.SortBtn_clicked)
        self.checkboxes = {self.ui.UniquesCheck: t.uniques, self.ui.UniqueMapsCheck: t.uni_maps,
                           self.ui.FragmentsCheck: t.fragments, self.ui.DivinationCheck: t.div_cards,
                           self.ui.FossilsCheck: t.fossils, self.ui.ResonatorsCheck: t.resonators,
                           self.ui.ScarabsCheck: t.scarabs, self.ui.OilsCheck: t.oils,
                           self.ui.IncubatorsCheck: t.incubators}
        self.open_file = open_file
        self.save_file = save_file
        self.all_strings = all_strings

    def SelectAllBtn_clicked(self):
        for checkbox in self.checkboxes.keys():
            if checkbox.isChecked() is False:
                checkbox.toggle()

    def RemoveAllBtn_clicked(self):
        for checkbox in self.checkboxes.keys():
            if checkbox.isChecked() is True:
                checkbox.toggle()

    def OpenFileBtn_clicked(self):
        self.open_file = QFileDialog.getOpenFileName(self, 'Open File',
                                                     osp.expanduser('~\\Documents\\My Games\\Path of Exile'),
                                                     filter='Lootfilter file(*.filter)')[0]
        try:
            file = open(self.open_file, 'r', encoding='utf-8')
            self.all_strings = t.tiers.open_filter(self.open_file)
            with file:
                self.ui.FilterName.setText(osp.basename(self.open_file))
                file.close()
        except:
            pass

    def SaveBtn_clicked(self):
        try:
            if self.ui.OverrideCheck.isChecked():
                shutil.copyfile('tmp.txt', self.open_file)
            else:
                self.save_file = QFileDialog.getSaveFileName(self, 'Save File',
                                                             osp.expanduser('~\\Documents\\My Games\\Path of Exile'),
                                                             filter='Lootfilter file(*.filter)')[0]
                shutil.copyfile('tmp.txt', self.save_file)
                print('Saved')
        except:
            pass

    def SortBtn_clicked(self):
        lines = dict()
        bases = dict()
        league = self.ui.League.currentText()
        Getdata().save_parser(league)
        print(f'Данные лиги {league} успешно загружены')
        for checkbox in self.checkboxes.keys():
            if checkbox.isChecked() is True:  # проверка чекбоксов на поставленные галочки
                # находим строки в файле фильтра:
                bases.update(self.checkboxes[checkbox].take_bases())
                lines.update(self.checkboxes[checkbox].find_lines())
        sorted = t.tiers.save_filter(lines, bases)  # сортировка найденных строк, замена данных и сохранение
        if lines == {}:
            print('Select category')
        else:
            print('Done')

    def mbox(self, body, title='Error'):
        dialog = QMessageBox(QMessageBox.Information, title, body)
        dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
