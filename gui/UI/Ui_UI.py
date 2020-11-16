# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\wolfeite\projectPy\heroage\EHCC4.0\project\health\overall\gui\UI\UI.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UI(object):
    def setupUi(self, UI):
        UI.setObjectName("UI")
        UI.resize(364, 115)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/Users/66964/.designer/backup/Data/Assets/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        UI.setWindowIcon(icon)
        self.centralWidget = QtWidgets.QWidget(UI)
        self.centralWidget.setObjectName("centralWidget")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(60, 20, 251, 41))
        font = QtGui.QFont()
        font.setFamily("Alef")
        font.setPointSize(22)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(60, 60, 161, 31))
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        UI.setCentralWidget(self.centralWidget)

        self.retranslateUi(UI)
        QtCore.QMetaObject.connectSlotsByName(UI)

    def retranslateUi(self, UI):
        _translate = QtCore.QCoreApplication.translate
        UI.setWindowTitle(_translate("UI", "中控后台系统V4.1"))
        self.label.setText(_translate("UI", "服务启动成功！"))
        self.label_2.setText(_translate("UI", "端口：4000"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    UI = QtWidgets.QMainWindow()
    ui = Ui_UI()
    ui.setupUi(UI)
    UI.show()
    sys.exit(app.exec_())
