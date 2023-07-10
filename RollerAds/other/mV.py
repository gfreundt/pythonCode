import os, json, sys
from datetime import datetime as dt
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def __init__(self):
        self.HEADERS = (
            "Name",
            "Filename",
            "Format",
            "Type",
            "Audio",
            "Duration",
            "Start Time/Date",
            "End Time/Date",
            "Active Now",
        )
        self.tableWidgets = []
        self.pushButtons = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1117, 904)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Active Table and its Buttons
        self.newTable(tableData=active, size=(40, 80, 921, 192))
        self.newButton(
            buttonName="UnQueue", label="UnQueue", size=(40, 280, 120, 30), tableNum=0
        )
        self.newButton(
            buttonName="PropertiesA",
            label="Edit Properties",
            size=(240, 280, 120, 30),
            tableNum=0,
        )
        self.newButton(
            buttonName="Up",
            label="Up",
            size=(380, 280, 40, 30),
            tableNum=0,
        )
        self.newButton(
            buttonName="Down",
            label="Down",
            size=(460, 280, 40, 30),
            tableNum=0,
        )

        # Inactive Table and its Buttons
        self.newTable(tableData=inactive, size=(40, 420, 921, 192))
        self.newButton(
            buttonName="UnQueue", label="Queue", size=(40, 620, 120, 30), tableNum=1
        )
        self.newButton(
            buttonName="PropertiesI",
            label="Edit Properties",
            size=(240, 620, 120, 30),
            tableNum=1,
        )
        self.newButton(
            buttonName="UnLoad", label="UnLoad", size=(440, 620, 120, 30), tableNum=1
        )

        self.newButton(
            buttonName="Up",
            label="Up",
            size=(580, 620, 40, 30),
            tableNum=0,
        )
        self.newButton(
            buttonName="Down",
            label="Down",
            size=(660, 620, 40, 30),
            tableNum=0,
        )

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1117, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def newButton(self, buttonName, label, size, tableNum):
        pushButton = QtWidgets.QPushButton(self.centralwidget)
        pushButton.setGeometry(QtCore.QRect(size[0], size[1], size[2], size[3]))
        pushButton.setObjectName(buttonName)
        pushButton.setText(QtCore.QCoreApplication.translate("MainWindow", label))
        pushButton.clicked.connect(lambda: self.clickme(tableNum, label))

        # Add new button to class buttons variable
        self.pushButtons.append(pushButton)

    def newTable(self, tableData, size):
        tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        tableWidget.setGeometry(QtCore.QRect(size[0], size[1], size[2], size[3]))
        tableWidget.setFrameShadow(QtWidgets.QFrame.Plain)
        tableWidget.setLineWidth(6)
        tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        tableWidget.setObjectName("pepito")
        tableWidget.setColumnCount(9)
        tableWidget.setRowCount(len(tableData))
        tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        for colNum, colTitle in enumerate(self.HEADERS):
            # Set Size of Column to Autosize
            tableWidget.horizontalHeader().setSectionResizeMode(
                colNum, QtWidgets.QHeaderView.ResizeToContents
            )
            # Create Column Header and Title Text
            item = QtWidgets.QTableWidgetItem()
            tableWidget.setHorizontalHeaderItem(colNum, item)
            tableWidget.horizontalHeaderItem(colNum).setText(
                QtCore.QCoreApplication.translate("MainWindow", colTitle)
            )
            for rowNum, _ in enumerate(tableData):
                if colNum == 0:
                    item = QtWidgets.QTableWidgetItem()
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    tableWidget.setVerticalHeaderItem(rowNum, item)
                    tableWidget.verticalHeaderItem(rowNum).setText(
                        QtCore.QCoreApplication.translate("MainWindow", str(rowNum + 1))
                    )
                item = tableWidget.setItem(rowNum, colNum, QtWidgets.QTableWidgetItem())
                tableWidget.item(rowNum, colNum).setText(
                    QtCore.QCoreApplication.translate(
                        "MainWindow", " " + str(active[rowNum][colNum]) + " "
                    )
                )
        tableWidget.horizontalHeader().setCascadingSectionResizes(False)

        # Add new table to class table variable
        self.tableWidgets.append(tableWidget)

    def clickme(self, tableNum, buttonAction):
        indexes = self.tableWidgets[tableNum].selectionModel().selectedRows()
        if not indexes:
            return
        else:
            row = indexes[0].row()
        print("click!", tableNum, indexes[0].row(), buttonAction)

        if buttonAction == "Up" and row > 0:
            print("go")

        self.tableWidgets[0].item(2, 2).setText(
            QtCore.QCoreApplication.translate("MainWindow", "perro")
        )

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))


def load_storyboard(static_directory):
    """Load JSON file that holds all media information"""
    with open(
        os.path.join(static_directory, "json", "storyboard_active_new.json"),
        mode="r",
    ) as json_file:
        storyboard = json.load(json_file)
        return trans(storyboard["active"]), trans(storyboard["inactive"])


def trans(data):
    return [
        [
            i["aka"],
            i["file_name"],
            i["format"],
            i["type"],
            str(i["audio"]),
            str(i["cycle_duration"]) + " s",
            i["datetime_start_str"],
            i["datetime_end_str"],
            "False",
        ]
        for i in data
    ]


if __name__ == "__main__":

    active, inactive = load_storyboard(r"C:\pythonCode\rollerAds\player\static")

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
