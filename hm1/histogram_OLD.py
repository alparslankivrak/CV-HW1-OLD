import sys
import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
from copy import copy, deepcopy
from PyQt5.QtWidgets import QApplication, QAction, qApp, QMainWindow
from PyQt5.QtWidgets import QWidget,QApplication,QTextEdit,QLabel,QPushButton,QVBoxLayout,QFileDialog,QHBoxLayout

from PyQt5 import QtCore, QtGui, QtWidgets


row_inp =0
column_inp =0
channel_inp =0
row_target =0
column_target =0
channel_target =0

sizes = (3, 256)
histogramArray_input = np.zeros(sizes)  # for bgr
histogramArray_target = np.zeros(sizes)  # for bgr
histogramArray_result = np.zeros(sizes) #for bgr result
class Histogram(QWidget):
    def __init__(self):

        super().__init__()

        self.init_ui()
    def init_ui(self):

        self.yazi_alani = QTextEdit()


        self.equalizer = QPushButton("Equalizer")


        h_box = QHBoxLayout()

#        h_box.addWidget(self.temizle)
#       h_box.addWidget(self.ac)
#      h_box.addWidget(self.kaydet)
        h_box.addWidget(self.equalizer)
        v_box = QVBoxLayout()

        v_box.addWidget(self.yazi_alani)

        v_box.addLayout(h_box)

        self.setLayout(v_box)

        self.setWindowTitle("Histogram")
        self.equalizer.clicked.connect(self.equalize_photos)

    def open_input_file(self):
        dosya_ismi = QFileDialog.getOpenFileName(self, "Dosya Aç", os.getenv("HOME"))

        img1 = cv2.imread(dosya_ismi[0],cv2.IMREAD_COLOR)
        global row_inp,column_inp,channel_inp
        row_inp, column_inp, channel_inp = img1.shape
        row = row_inp
        column = column_inp
        # cevirmeden
        global histogramArray_input
        for i in range(0, row):
            for j in range(0, column):
                histogramArray_input[0, img1[i, j, 0]] += 1    #blue
                histogramArray_input[1, img1[i, j, 1]] += 1    #green
                histogramArray_input[2, img1[i, j, 2]] += 1    #red
        #print(histogramArray_input)
        #plt.plot(histogramArray_input[0],color='blue')
        #plt.plot(histogramArray_input[1], color='green')
        #plt.plot(histogramArray_input[2], color='red')
        #plt.show()
        print("Open Inputa basıldı.")

    def open_target_file(self):
        dosya_ismi = QFileDialog.getOpenFileName(self, "Dosya Aç", os.getenv("HOME"))
        global img2
        img2 = cv2.imread(dosya_ismi[0],cv2.IMREAD_COLOR)
        global row_target, column_target, channel_target
        row_target, column_target, channel_target = img2.shape
        row = row_target
        column = column_target
        # cevirmeden
        global histogramArray_target
        sizes = (3,256)
        histogramArray = np.zeros(sizes) # for bgr
        for i in range(0, row):
            for j in range(0, column):
                histogramArray_target[0, img2[i, j,0]] += 1    #blue
                histogramArray_target[1, img2[i, j, 1]] += 1    #green
                histogramArray_target[2, img2[i, j, 2]] += 1    #red
        #plt.plot(histogramArray_target[0],color='blue')
        #plt.plot(histogramArray_target[1], color='green')
        #plt.plot(histogramArray_target[2], color='red')
    #    plt.show()
        print("Open Target File basıldı.")

    def save_file(self):
        print("Save File basıldı.")


    def equalize_photos(self):
        global histogramArray_result, row_inp, column_inp, row_target, column_target
        temp_input =deepcopy( histogramArray_input)
        temp_target = deepcopy(histogramArray_target)
        # cumulative ve oranını alma islemi

        temp_input = self.take_cumulative(temp_input)
        temp_input = self.take_ratio(temp_input, row_inp,column_inp)
        temp_target = self.take_cumulative(temp_target)
        temp_target =self.take_ratio(temp_target, row_target,column_target)
        print("FLAG 1")
        #LOOK UP TABLE
        lut = self.create_lut(temp_input, temp_target)
        print("FLAG 1")
       # print(histogramArray_input)
        #getting lut back
    #    lut = self.cdf_to_pdf(lut, row_target, column_target)
        #########
        new_image = np.zeros((row_inp, column_inp, 3))

        print("FLAG 1")
        img_new = cv2.imread('color2.png')
        print(row_inp)
        print(column_inp)
        for i in range(0,row_inp):
            for j in range(0,column_inp):

                new_image[i, j, 0] = int(lut[0, int(img_new[i, j, 0])])
                new_image[i, j, 1] = int(lut[1, int(img_new[i, j, 1])])
                new_image[i, j, 2] = int(lut[2, int(img_new[i, j, 2])])

        k=np.uint8(new_image)

        for i in range(0, row_inp):
            for j in range(0, column_inp):
                histogramArray_result[0, int(new_image[i, j, 0])] += 1    #blue
                histogramArray_result[1, int(new_image[i, j, 1])] += 1    #green
                histogramArray_result[2,int(new_image[i, j, 2])] += 1    #red

        self.draw_figures(k, histogramArray_result)


        '''

        '''
        print("Equalizea basıldı.")



    def take_cumulative(self,arr):
        for i in range(1,256):
            arr[0, i] += arr[0, i-1]
            arr[1, i] += arr[1, i-1]
            arr[2, i] += arr[2, i-1]
        return arr

    def take_ratio(self,arr,r,c):
        for x in range(0,256):
            arr[0,x] = arr[0, x] / (r*c)
            arr[1, x] = arr[1, x] / (r * c)
            arr[2, x] = arr[2, x] / (r * c)
        return arr

    def create_lut(self, inp, target):
        temp_lut = np.zeros(sizes)
        gj_b = 0
        gj_g = 0
        gj_r = 0
        for gi in range(0, 256):
            while target[0, gj_b] < inp[0, gi] and gj_b < 256:
                gj_b += 1
            while target[1, gj_g] < inp[1, gi] and gj_g < 256:
                gj_g += 1
            while target[2, gj_r] < inp[2, gi] and gj_r < 256:
                gj_r += 1
            temp_lut[0, gi] = gj_b
            temp_lut[1, gi] = gj_g
            temp_lut[2, gi] = gj_r
        return temp_lut

    def draw_figures(self,img,hist):
        plt.subplot(4,1,1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.subplot(4,1,2)
        plt.plot(hist[0],color='blue')
        plt.subplot(4, 1, 3)
        plt.plot(hist[1],color='green')
        plt.subplot(4, 1, 4)
        plt.plot(hist[2],color='red')
        plt.show()

class Ui_mainWindow(object):


    def setupUi(self, mainWindow):

        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(815, 484)

        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.input_box = QtWidgets.QGroupBox(self.centralwidget)
        self.input_box.setGeometry(QtCore.QRect(10, 20, 435, 620))
        self.input_box.setMouseTracking(False)
        self.input_box.setAutoFillBackground(False)
        self.input_box.setFlat(False)
        self.input_box.setCheckable(False)
        self.input_box.setObjectName("input_box")
        self.target_box = QtWidgets.QGroupBox(self.centralwidget)
        self.target_box.setGeometry(QtCore.QRect(460, 20, 435, 620))
        self.target_box.setObjectName("target_box")
        self.result_box = QtWidgets.QGroupBox(self.centralwidget)
        self.result_box.setGeometry(QtCore.QRect(910, 20, 435, 620))
        self.result_box.setObjectName("result_box")
        self.pushButtpn_equalize = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtpn_equalize.setGeometry(QtCore.QRect(10, 0, 1201, 21))
        self.pushButtpn_equalize.setAutoDefault(False)
        self.pushButtpn_equalize.setDefault(False)
        self.pushButtpn_equalize.setFlat(False)
        self.pushButtpn_equalize.setObjectName("pushButtpn_equalize")
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 815, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Input_File = QtWidgets.QAction(mainWindow)
        self.actionOpen_Input_File.setObjectName("actionOpen_Input_File")
        self.actionOpen_Target = QtWidgets.QAction(mainWindow)
        self.actionOpen_Target.setObjectName("actionOpen_Target")
        self.actionSave = QtWidgets.QAction(mainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionExit = QtWidgets.QAction(mainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen_Input_File)
        self.menuFile.addAction(self.actionOpen_Target)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

        self.menuFile.triggered.connect(self.response)()

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "HistogramApp"))
        self.input_box.setTitle(_translate("mainWindow", "INPUT"))
        self.target_box.setTitle(_translate("mainWindow", "TARGET"))
        self.result_box.setTitle(_translate("mainWindow", "RESULT"))
        self.pushButtpn_equalize.setText(_translate("mainWindow", "Equalize Histogram"))
        self.menuFile.setTitle(_translate("mainWindow", "File"))
        self.actionOpen_Input_File.setText(_translate("mainWindow", "Open Input File"))
        self.actionOpen_Target.setText(_translate("mainWindow", "Open Target"))
        self.actionSave.setText(_translate("mainWindow", "Save"))
        self.actionExit.setText(_translate("mainWindow", "Exit"))

    def response(self, action):

        if action.text() == "Open Input File":
            self.set_input_image()
            #self.window.open_input_file()
        elif action.text() == "Open Target File":
            self.window.open_target_file()
        elif action.text() == "Save File":
            self.window.save_file()
        elif action.text() == "Exit":
            print("Exita basıldı.")
            qApp.quit()

    def set_input_image(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", "",
                                                            "Image Files (*.png *.jpg *jpeg *.bmp)")  # Ask for file
        if fileName:  # If the user gives a file
            pixmap = QtGui.QPixmap(fileName)  # Setup pixmap with the provided image
            pixmap = pixmap.scaled(self.input_box.width(), self.input_box.height(), QtCore.Qt.KeepAspectRatio)  # Scale pixmap
            self.imageLbl.setPixmap(pixmap)  # Set the pixmap onto the label
            self.imageLbl.setAlignment(QtCore.Qt.AlignCenter)  # Align the label to center

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()

    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

