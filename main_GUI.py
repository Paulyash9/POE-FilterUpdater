import sys
import os.path as osp
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GUI.GUI_2 import *
import tiers


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, file='', parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.SelectAllBtn.clicked.connect(self.SelectAllBtn_clicked)
        self.ui.RemoveAllBtn.clicked.connect(self.RemoveAllBtn_clicked)
        self.ui.OpenFileBtn.clicked.connect(self.OpenFileBtn_clicked)
        self.ui.SaveBtn.clicked.connect(self.SaveBtn_clicked)
        self.ui.SortBtn.clicked.connect(self.SortBtn_clicked)
        self.checkboxes = {self.ui.UniquesCheck: tiers.uniques, self.ui.UniqueMapsCheck: tiers.uni_maps,
                           self.ui.FragmentsCheck: tiers.fragments, self.ui.DivinationCheck: tiers.div_cards,
                           self.ui.FossilsCheck: tiers.fossils, self.ui.ResonatorsCheck: tiers.resonators,
                           self.ui.ScarabsCheck: tiers.scarabs, self.ui.OilsCheck: tiers.oils,
                           self.ui.IncubatorsCheck: tiers.incubators}
        self.file = file

    def SelectAllBtn_clicked(self):
        for checkbox in self.checkboxes.keys():
            if checkbox.isChecked() is False:
                checkbox.toggle()

    def RemoveAllBtn_clicked(self):
        for checkbox in self.checkboxes.keys():
            if checkbox.isChecked() is True:
                checkbox.toggle()

    def OpenFileBtn_clicked(self):
        self.file = QFileDialog.getOpenFileName(self, 'Open File',
                                                osp.expanduser('~\\Documents\\My Games\\Path of Exile'),
                                                filter='Lootfilter file(*.filter)')[0]
        try:
            file = open(self.file, 'r', encoding='utf-8')
            with file:
                self.ui.FilterName.setText(osp.basename(self.file))
                file.close()
                print(osp.abspath(self.file))
                return osp.abspath(self.file)
        except:
            pass

    def SaveBtn_clicked(self):
        pass

    def SortBtn_clicked(self):
        lines = dict()
        try:
            for checkbox in self.checkboxes.keys():
                if checkbox.isChecked() is True:
                    #  находим строки в файле фильтра
                    lines.update(self.checkboxes[checkbox].find_lines(osp.abspath(self.file)))
            # сортировка номеров строк по возрастанию:
            lines = {k: v for k, v in sorted(lines.items(), key=lambda item: item[1])}
            print(lines)

        except:
            pass

    def mbox(self, body, title='Error'):
        dialog = QMessageBox(QMessageBox.Information, title, body)
        dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
