import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from gui.helpers.func_helper import get_expired


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

    print(get_expired(1710121097))
    # cmd ='''powershell -Command "(Get-ChildItem | Sort-Object { [regex]::Replace($_.Name, '\d+', { $args[0].Value.PadLeft(20) }) }).Name"'''
    # process = subprocess.Popen(cmd, shell=True,
    #                            cwd='E:\\Project\\Python\\NTSVideoCreator\\test\\2',
    #                            stdout=subprocess.PIPE,
    #                            stderr=subprocess.PIPE)
    # out = process.communicate()[0].decode('ascii').split('\r\n')
    # # wait for the process to termina
    # print(out)

    # from elevenlabs import generate, play
    #
    # audio = generate(
    #     voice="Adam"
    #     # @param ["Adam", "Antoni", "Arnold", "Bill", "Callum", "Charlie", "Charlotte", "Clyde", "Daniel", "Dave", "Domi", "Dorothy", "Drew", "Elli", "Emily", "Ethan", "Fin", "Freya", "George", "Gigi", "Giovanni", "Glinda", "Grace", "Harry", "James", "Jeremy", "Jessie", "Joseph", "Joch", "Liam", "Lily", "Matilda", "Michael", "Mimi", "Nicole", "Patrick", "Paul", "Rachel", "Sam", "Sarah", "Serena", "Thomas"] {allow-input: false}
    #     ,
    #     text="Votre Texte"  # @param [] {allow-input: true}
    #     ,
    #     model='eleven_multilingual_v2'
    # )
    #
    # play(audio, notebook=True)