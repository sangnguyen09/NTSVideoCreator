import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Item Image to TableView Example")

        self.tableview = QTableView()
        self.setCentralWidget(self.tableview)

        model = QStandardItemModel(4, 2)
        self.tableview.setModel(model)

        for row in range(4):
            for col in range(2):
                item = QStandardItem()
                if col == 0:  # Add image to the first column
                    pixmap = QPixmap("1.png")  # Replace "image.png" with the path to your image
                    item.setData(pixmap, Qt.DecorationRole)
                else:
                    item.setData("Item ({}, {})".format(row, col), Qt.DisplayRole)
                model.setItem(row, col, item)

if __name__ == '__main__':
    cmd ='''powershell -Command "(Get-ChildItem | Sort-Object { [regex]::Replace($_.Name, '\d+', { $args[0].Value.PadLeft(20) }) }).Name"'''
    process = subprocess.Popen(cmd, shell=True,
                               cwd='E:\\Project\\Python\\NTSVideoCreator\\test\\2',
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out = process.communicate()[0].decode('ascii').split('\r\n')
    # wait for the process to termina
    print(out)
