# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ds1.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
ui1 = "abc"

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(256, 179)
        self.Master = QtWidgets.QPushButton(Form)
        self.Master.setGeometry(QtCore.QRect(70, 80, 91, 31))
        self.Master.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Master.setToolTipDuration(2)
        self.Master.setAutoFillBackground(False)
        self.Master.setAutoDefault(True)
        self.Master.setFlat(False)
        self.Master.setObjectName("Master")
        self.Client = QtWidgets.QPushButton(Form)
        self.Client.setGeometry(QtCore.QRect(70, 120, 91, 31))
        self.Client.setObjectName("Client")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(70, 50, 91, 16))
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.Master.setToolTip(_translate("Form", "Start a new Download by providing Link"))
        self.Master.setText(_translate("Form", "Start Download"))
        self.Client.setText(_translate("Form", "Serve Download"))
        self.label.setText(_translate("Form", "Use this system to"))

def abc():
	ui1.label.setText("abc")
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    ui1 = ui
    ui.Master.clicked.connect(abc)
    ui.Client.clicked.connect(abc)
    Form.show()
    sys.exit(app.exec_())
