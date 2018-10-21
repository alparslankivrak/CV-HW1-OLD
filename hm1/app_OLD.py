import sys

from PyQt5 import QtWidgets



def Window():

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()

    window.setWindowTitle("Histogram Matching Application")

    window.setGeometry(50,50,1200,650)

    button = QtWidgets.QPushButton(window)\
        .setText("Equalize Histogram")

    window.show()



    sys.exit(app.exec_())

Window()