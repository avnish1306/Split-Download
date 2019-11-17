import ds1,ds1,ds3
from PyQt5 import QtCore, QtGui, QtWidgets
ui1 = "abc"
def abc():
	ui1.label.setText("abc")
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = ds1.Ui_Form()
    ui.setupUi(Form)
    ui1 = ui
    ui.Master.clicked.connect(abc)
    ui.Client.clicked.connect(abc)
    Form.show()
    sys.exit(app.exec_())