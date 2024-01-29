from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, \
    QTableWidget, QHeaderView, \
    QStyle

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
# IMPORT STYLE
# ///////////////////////////////////////////////////////////////
from .style import *


# PY PUSH BUTTON
# ///////////////////////////////////////////////////////////////


class TableMainWidget(QWidget):
    def __init__(self):
        super().__init__()
        # SET STYLESHEET
        self.is_check_all = False #trạng thái checkbok ban đầu là chưa check
        self.icon_checked = QIcon(ConfigResource.set_svg_icon("checked.png"))
        self.icon_unchecked = QIcon(ConfigResource.set_svg_icon("uncheck.png"))

        self.init_ui()
    def init_ui(self):
        self.create_widgets()
        self.set_stylesheet(
            radius=8,
            color = ConfigTheme().app_color["text_foreground"],
            selection_color = ConfigTheme().app_color["context_color"],
            bg_color = ConfigTheme().app_color["bg_two"],
            header_horizontal_color = ConfigTheme().app_color["dark_two"],
            header_vertical_color = ConfigTheme().app_color["bg_three"],
            bottom_line_color = ConfigTheme().app_color["bg_three"],
            grid_line_color = ConfigTheme().app_color["bg_one"],
            scroll_bar_bg_color = ConfigTheme().app_color["bg_one"],
            scroll_bar_btn_color = ConfigTheme().app_color["dark_four"],
            context_color = ConfigTheme().app_color["context_color"]
        )
        self.create_layouts()
        self.add_widgets_to_layouts()

        self.setup_table()
        #show dư liệu
        self.displayTable()

        self.setup_connections()


    def create_widgets(self):
        self.main_table = QTableWidget()

        #tạo Nút CheckBox trên tiêu đề
        self.icon_check_all = QIcon(ConfigResource.set_svg_icon("uncheck.png"))

        #menu ngữ cảnh
        self.menu = QMenu()

        setting_icon = self.style().standardIcon(QStyle.SP_DriveDVDIcon)
        self.act_setting = self.menu.addAction(setting_icon,"Cài đặt")  #(QAction('test'))
        self.act_setting.setShortcut("Ctrl+O")

        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.act_play = self.menu.addAction(play_icon,"Bắt đầu")
        self.act_play.setShortcut("Ctrl+P")

        stop_icon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.act_stop = self.menu.addAction(stop_icon,"Dừng")
        self.act_stop.setShortcut("Ctrl+S")

    def setup_table(self):
        #========== Cài đặt cho table============
        self.main_table.setColumnCount(5) # số lường cột
        self.main_table.verticalHeader().setVisible(False)# ko hiện số thứ tự ở các dòng
        self.main_table.setFocusPolicy(Qt.FocusPolicy.NoFocus) #cái này là khi focus vào thì ko hiện cái viền
        # self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) #cái này là ko cho bấm vào chọn
        self.main_table.horizontalHeader().setHighlightSections(False) # không Highlight khi chọn vào tiêu đề
        # self.main_table.horizontalHeader().setSectionsClickable(True)
        # QHeaderView.setSectionsClickable()

        self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # cho phép chọn thành dòng
        self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # không cho edit

        #tao menucontext
        self.main_table.viewport().installEventFilter(self)
        self.main_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.main_table.customContextMenuRequested.connect(self.generateMenu)

        # self.main_table.setRowCount(5)# số lường dòng
        # self.main_table.setColumnHidden(0,True) # ẩn cột Product Id

        #==================Thiết lập tên cột ========
        self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_check_all,""))

        self.main_table.setHorizontalHeaderItem(1,QTableWidgetItem("Name"))
        self.main_table.setHorizontalHeaderItem(2,QTableWidgetItem("Surname"))
        self.main_table.setHorizontalHeaderItem(3,QTableWidgetItem("Address"))
        self.main_table.setHorizontalHeaderItem(4,QTableWidgetItem("Chức năng"))

        self.main_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents) #gian cách vừa với content
        self.main_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch) #gian cách đều
        self.main_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch) #gian cách đều
        self.main_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.Stretch)
        self.main_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeMode.ResizeToContents)


    def setup_connections(self):
        ##==================Các sự kiện của table ========
        self.main_table.cellDoubleClicked.connect(self.cellDoubleClicked) # nhận đc row và colum
        self.main_table.itemDoubleClicked.connect(self.itemDoubleClicked) # nhận đc item
        self.main_table.itemSelectionChanged.connect(self.removeAllCheckedItem) # nhận đc item
        # self.main_table.horizontalHeader().sectionPressed.disconnect()
        self.main_table.horizontalHeader().sectionPressed.connect(self.onHeaderClicked)        #bắt sự kiện ng dùng nhấn vào tiêu đề
        # self.main_table.selectionChanged

        #========== Các sự kiện cho menu contentext ============
        self.act_setting.triggered.connect(self.signal_setting)
        self.act_play.triggered.connect(self.signal_play)
        self.act_stop.triggered.connect(self.signal_stop)

    def signal_setting(self):
        print("signal_setting")

    def signal_play(self):
        print("signal_play")

    def signal_stop(self):
        print("signal_stop")

    def create_layouts(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0,0,0,0)

    def add_widgets_to_layouts(self):
        self.widget_layout.addWidget(self.main_table)

    def displayTable(self):
        self.main_table.setFont(QFont("Times",12))
        for i in reversed(range(self.main_table.rowCount())):
            self.main_table.removeRow(i)

        listItem = [
            {
                "name": "Sang 1",
                "surname": "Thanh 1",
                "address": "Quân 1"
            },{
                "name": "Sang 2",
                "surname": "Thanh 2",
                "address": "Quân 2"
            },
            {
                "name": "Sang 3",
                "surname": "Thanh 3",
                "address": "Quân 3"
            },  {
                "name": "Sang 3",
                "surname": "Thanh 3",
                "address": "Quân 3"
            },  {
                "name": "Sang 3",
                "surname": "Thanh 3",
                "address": "Quân 3"
            },
        ]
        for row_data in listItem:
            row_number = self.main_table.rowCount() #lấy ra số dòng hiện tại
            self.main_table.insertRow(row_number) #thêm số dòng


            #============== thêm nút chức năng=======

            #thêm trường checkbox vào đầu
            # widget  = QWidget()
            # layoutCheckbox = QHBoxLayout(widget )
            # widget.checkbox =  QCheckBox()
            # widget.checkbox.clicked.connect(self.removeAllSelectedItem)
            # widget.checkbox.stateChanged.connect(self.stateChangedCheckbox)
            # layoutCheckbox.addWidget(widget.checkbox)
            # layoutCheckbox.setAlignment(Qt.AlignCenter)
            # layoutCheckbox.setContentsMargins(0,0,0,0)
            # widget.setLayout(layoutCheckbox)
            # self.main_table.setCellWidget(row_number,0, widget)
            item = self.itemCheckboxTable(row_number,False)
            self.main_table.setItem(row_number,0,item)


            #thêm trường button vào cuối
            self.btn=  QPushButton('Stop')
            self.btn.setStyleSheet("background-color: rgb(255, 128, 128); padding:0")
            self.btn.setContentsMargins(0,0,0,0)
            self.main_table.setCellWidget(row_number,4, self.btn)
            self.btn.clicked.connect(self.getRowColumn)


            #============== cho hiện dữ liệu =======
            for column_number, data in enumerate(row_data): #lặp dictionary
                item = QTableWidgetItem(row_data[data])
                if  row_number % 2 == 0:
                    item.setBackground(QColor(91, 91, 91))
                else:
                    item.setBackground(QColor(135, 135, 135))

                self.main_table.setItem(row_number,column_number+1,item)
    def itemCheckboxTable(self,row_number, isCheck):
        icon =""
        if isCheck:
            icon = self.icon_checked
        else:
            icon = self.icon_unchecked

        item = QTableWidgetItem(icon,"")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if  row_number % 2 == 0:
            item.setBackground(QColor(91, 91, 91))
        else:
            item.setBackground(QColor(135, 135, 135))
        return item
    # sự kiện cho context menu
    def eventFilter(self, source, event):
        if(event.type() == QEvent.Type.MouseButtonPress and
                event.buttons() == Qt.MouseButton.RightButton and
                source is self.main_table.viewport()):
            item = self.main_table.itemAt(event.pos())
            # print('Global Pos:', event.globalPos())
            if item is not None:
                print('Menu contenxt Table Item:', item.row(), item.column())

                #menu.exec_(event.globalPos())
        return super().eventFilter(source, event)
    def generateMenu(self, pos):
        x = pos.x() + 10
        y = pos.y() +30
        self.menu.exec(self.main_table.mapToGlobal(QPoint(x,y)))


    def listRowChecked(self): #lấy ra các dòng được tích vào
        checked_list = []
        selected_list = []
        for i in range(self.main_table.rowCount()):
            if self.main_table.cellWidget(i, 0).checkbox.isChecked(): #checkbox là biến ở trên lúc add vào table
                checked_list.append(i)
            else:
                pass
        for item in self.main_table.selectionModel().selectedRows():
            selected_list.append(item.row())
        return checked_list ,selected_list

    def getRowColumn(self):
        for item in self.main_table.selectedIndexes():
            
            print(item.row(),item.column() )

    def deselectRow(self, row):
        if row > self.main_table.rowCount() - 1:
            return
        selectionModel = self.main_table.selectionModel()
        selectionModel.select(self.main_table.model().index(row, 0),
                          selectionModel.Deselect|selectionModel.Rows)

    def removeAllCheckedItem(self):

        self.rows = []
        for it in self.main_table.selectionModel().selectedRows():
            
            if it.row() not in self.rows:
                self.rows.append(it.row())
            else:
                self.rows.remove(it.row())
        for i in range(self.main_table.rowCount()):
                if i in self.rows:
                    item = self.itemCheckboxTable(i,True)

                    self.main_table.setItem(i, 0,item)
                else:
                    item = self.itemCheckboxTable(i,False)
                    self.main_table.setItem(i, 0,item)

        if len(self.rows) == self.main_table.rowCount():
            self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_checked,""))
            self.is_check_all = True
        else:

            self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_unchecked,""))
            self.is_check_all = False

    def onHeaderClicked(self,logicalIndex):
        if logicalIndex == 0:
            self.is_check_all = not self.is_check_all
            if self.is_check_all:
                self.main_table.horizontalHeaderItem(0).setIcon(self.icon_checked)
                # self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_checked,""))
                self.main_table.selectAll()
            else:
                self.main_table.horizontalHeaderItem(0).setIcon(self.icon_unchecked)
                # self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_unchecked,""))
                self.main_table.clearSelection()


    def cellDoubleClicked(self, row, cl):
        print("cellDoubleClicked "+ str(row))
        print("cellDoubleClicked "+ str(cl))

    def itemDoubleClicked(self, item):
        print(item)

    # SET STYLESHEET
    def set_stylesheet(
        self,
        radius,
        color,
        bg_color,
        header_horizontal_color,
        header_vertical_color,
        selection_color,
        bottom_line_color,
        grid_line_color,
        scroll_bar_bg_color,
        scroll_bar_btn_color,
        context_color
    ):
        # APPLY STYLESHEET
        style_format = style.format(
            _radius = radius,          
            _color = color,
            _bg_color = bg_color,
            _header_horizontal_color = header_horizontal_color,
            _header_vertical_color = header_vertical_color,
            _selection_color = selection_color,
            _bottom_line_color = bottom_line_color,
            _grid_line_color = grid_line_color,
            _scroll_bar_bg_color = scroll_bar_bg_color,
            _scroll_bar_btn_color = scroll_bar_btn_color,
            _context_color = context_color
        )
        self.main_table.setStyleSheet(style_format)
#kiem tra khi dung wedgetcheckbox
# for i in range(self.main_table.rowCount()):
#     if i in self.rows:
#         self.main_table.cellWidget(i, 0).checkbox.setChecked(True)
#     else:
#         self.main_table.cellWidget(i, 0).checkbox.setChecked(False)