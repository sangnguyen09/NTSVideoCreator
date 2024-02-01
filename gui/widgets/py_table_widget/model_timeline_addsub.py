from enum import Enum

from PySide6.QtCore import Qt, QAbstractTableModel, Slot, QModelIndex
from PySide6.QtGui import QColor, QFont, QPixmap

from gui.helpers.constants import get_color_do_lech_sub


class ColumnNumberTabEdit(Enum):
    column_avatar = 0
    column_original = 1
    column_translated = 2


class ColumnNumber(Enum):
    column_chuc_nang = 0
    # column_do_lech = 1
    # column_time = 2
    column_sub_text = 1

class TableAddModel(QAbstractTableModel):
    def __init__(self, data, name_column):
        super(TableAddModel, self).__init__()
        # print(data)
        self.__data: list = data
        self.columns = name_column

    @property
    def update_data(self):
        return self.__data

    @update_data.setter
    def update_data(self, df):
        self.beginResetModel()
        self.__data = df.copy()
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        # for setting columns name
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        # # for setting rows name
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return f"No. {section + 1}"

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.EditRole:

            row, column = index.row(), index.column()
            if column == ColumnNumber.column_chuc_nang.value:
                return False
            self.__data[row][column] = value
            # print("edit", value)

            self.dataChanged.emit(
                index, index, (Qt.EditRole,)
            )
        elif role == Qt.BackgroundRole:
            # print("BackgroundRole", value)

            self.dataChanged.emit(index, index, [role])
        elif role == Qt.ForegroundRole:
            # print("ForegroundRole", value)

            self.dataChanged.emit(index, index, [role])

        else:
            return False
        return True

    @Slot()
    def update_item(self, row, col, value, role=Qt.EditRole):
        ix = self.index(row, col)
        self.setData(ix, value, role)

    @Slot()
    def update_list_item(self, list_data, role=Qt.EditRole):
        for data in list_data:
            row, col, value = data
            self.__data[row][col] = value
        self.layoutChanged.emit()

    @Slot()
    def resetDataColumn(self, col, role=Qt.EditRole):
        for row in range(self.rowCount()):
            self.__data[row][col] = ""
        self.layoutChanged.emit()

    def insertRows(self, position, rows=1, index=QModelIndex()):
        # print('insertRows')

        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.__data.insert(position + row, ["", ""])
        # self.added += 1
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        # print('removeRows')
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        self.__data = self.__data[:position] + self.__data[position + rows:]
        self.endRemoveRows()

        return True

    def data(self, index, role=Qt.DisplayRole):

        if index.isValid():

            if role == Qt.DisplayRole or role == Qt.EditRole:
                row, column = index.row(), index.column()
                value = self.__data[row][column]

                if column == ColumnNumber.column_chuc_nang.value:
                    value = "PREVIEW"

                return str(value)

            elif role == Qt.FontRole:
                row, column = index.row(), index.column()
                if column == ColumnNumber.column_sub_text.value:
                    # print('vaoffff')
                    font = QFont()
                    font.setPixelSize(18)
                    return font


            elif role == Qt.ForegroundRole:
                try:
                    row, column = index.row(), index.column()
                    if column == ColumnNumber.column_do_lech.value:
                        value = self.__data[row][column]
                        if value == "":
                            value = 0
                        # if column == 0:
                        return QColor(get_color_do_lech_sub(float(value)))

                    elif column == ColumnNumber.column_chuc_nang.value:
                        return QColor("#6eff0d")
                except:
                    pass
    def getData(self):
        return self.__data
    def rowCount(self, parent=QModelIndex()):
        # The length of the outer list.
        return len(self.__data)

    def columnCount(self, parent=QModelIndex()):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.__data[0])


class TableEditModel(QAbstractTableModel):
    def __init__(self, data, name_column):
        super(TableEditModel, self).__init__()
        self.__data: list = data
        self.columns = name_column
        self.font_size_table = 18
        self.color_table = '#ffffff'

    @property
    def update_data(self):
        return self.__data

    @update_data.setter
    def update_data(self, df):
        self.beginResetModel()
        self.__data = df.copy()
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        # for setting columns name
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        # # for setting rows name
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return f"No. {section + 1}"

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.EditRole:

            row, column = index.row(), index.column()

            self.__data[row][column] = value
            # print("edit", value)

            self.dataChanged.emit(
                index, index, (Qt.EditRole,)
            )
        elif role == Qt.BackgroundRole:
            # print("BackgroundRole", value)

            self.dataChanged.emit(index, index, [role])
        elif role == Qt.ForegroundRole:
            # print("ForegroundRole", value)

            self.dataChanged.emit(index, index, [role])

        else:
            return False
        return True

    @Slot()
    def update_item(self, row, col, value, role=Qt.EditRole):
        ix = self.index(row, col)
        self.setData(ix, value, role)

    @Slot()
    def update_list_item(self, list_data, role=Qt.EditRole):
        for data in list_data:
            row, col, value = data
            self.__data[row][col] = value
        self.layoutChanged.emit()

    @Slot()
    def resetDataColumn(self, col, role=Qt.EditRole):
        for row in range(self.rowCount()):
            self.__data[row][col] = ""
        self.layoutChanged.emit()

    def insertRows(self, position, rows=1, index=QModelIndex()):
        # print('insertRows')

        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.__data.insert(position + row, ["", "", "", "", "", ""])
        # self.added += 1
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        # print('removeRows')
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        self.__data = self.__data[:position] + self.__data[position + rows:]
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    # def removeListRow (self, position, rows=1, index=QModelIndex()):
    # 	# print('removeRows')
    # 	self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
    #
    # 	self.__data = self.__data[:position] + self.__data[position + rows:]
    # 	self.endRemoveRows()
    # 	self.layoutChanged.emit()
    # 	return True

    def update_font(self, value):
        self.font_size_table = value

    def update_color(self, value):
        self.color_table = value

    def data(self, index, role=Qt.DisplayRole):

        if index.isValid():

            if role == Qt.DisplayRole or role == Qt.EditRole:
                row, column = index.row(), index.column()
                value = self.__data[row][column]
                if column == ColumnNumberTabEdit.column_avatar.value:
                    return ""
                return str(value)

            elif role == Qt.FontRole:
                row, column = index.row(), index.column()
                if column == ColumnNumberTabEdit.column_translated.value or column == ColumnNumberTabEdit.column_original.value:
                    # print('vaoffff')
                    font = QFont()
                    font.setPixelSize(self.font_size_table)
                    return font
            elif role == Qt.DecorationRole:
                row, column = index.row(), index.column()
                if column == ColumnNumberTabEdit.column_avatar.value:
                    value = self.__data[row][column]
                    pixmap = QPixmap(value)
                    pixmap = pixmap.scaled(100,100)
                    return pixmap

            elif role == Qt.ForegroundRole:
                try:
                    # row, column = index.row(), index.column()

                    return QColor(self.color_table)

                except:
                    pass

    #
    # elif role == Qt.ForegroundRole:
    # 	try:
    # 		row, column = index.row(), index.column()
    # 		if column == ColumnNumber.column_do_lech.value:
    # 			value = self.__data[row][column]
    # 			if value == "":
    # 				value = 0
    # 			# if column == 0:
    # 			return QColor(get_color_do_lech_sub(float(value)))
    #
    # 		elif column == ColumnNumber.column_chuc_nang.value:
    # 			value = self.__data[row][column]
    # 			if value.lower() == "preview":
    # 				return QColor("#6eff0d")
    # 	except:
    # 		pass
    def getData(self):
        return self.__data
    def rowCount(self, parent=QModelIndex()):
        # The length of the outer list.
        return len(self.__data)

    def columnCount(self, parent=QModelIndex()):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.__data[0])
