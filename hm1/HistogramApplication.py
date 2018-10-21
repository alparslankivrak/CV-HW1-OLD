import sys
import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
from copy import copy, deepcopy
from PyQt5.QtWidgets import QApplication, QAction, qApp, QMainWindow
from PyQt5.QtWidgets import QWidget, QApplication, QTextEdit, QLabel, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

row_inp = 0
column_inp = 0
channel_inp = 0
row_target = 0
column_target = 0
channel_target = 0

sizes = (3, 256)
histogramArray_input = np.zeros(sizes)  # for bgr
histogramArray_target = np.zeros(sizes)  # for bgr
histogramArray_result = np.zeros(sizes)  # for bgr result
img_new = cv2.imread('color2.png')
class Histogram(QWidget):
    def __init__(self):

        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setObjectName("mainWindow")
        self.resize(800, 600)

        centralwidget = QtWidgets.QWidget(self)
        centralwidget.setObjectName("centralwidget")
        input_box = QtWidgets.QGroupBox(centralwidget)
        input_box.setGeometry(QtCore.QRect(10, 20, 435, 620))
        input_box.setObjectName("input_box")
        target_box = QtWidgets.QGroupBox(centralwidget)
        target_box.setGeometry(QtCore.QRect(460, 20, 435, 620))
        target_box.setObjectName("target_box")
        result_box = QtWidgets.QGroupBox(centralwidget)
        result_box.setGeometry(QtCore.QRect(910, 20, 435, 620))
        result_box.setObjectName("result_box")
        pushbutton_equalize = QtWidgets.QPushButton(centralwidget)
        pushbutton_equalize.setGeometry(QtCore.QRect(10, 0, 1201, 21))
        pushbutton_equalize.setObjectName("pushButtpn_equalize")
        input_box.setTitle("INPUT")
        target_box.setTitle("TARGET")
        result_box.setTitle("RESULT")
        self.setWindowTitle("HistogramApp")
        pushbutton_equalize.setText("Equalize Histogram")
        '''
        img1 = QtWidgets.QLabel(centralwidget)
        img1.setGeometry(20, 20, 500,500 )
        img1.setFrameShape(QtWidgets.QFrame.Box)
        img1.setText("")
        img1.setObjectName("image1")
        '''

        pushbutton_equalize.clicked.connect(self.equalize_photos)

    def open_input_file(self):
        global img_new
        dosya_ismi = QFileDialog.getOpenFileName(self, "Dosya Aç","","Image Files (*.png *.jpg *jpeg *.bmp)", os.getenv("HOME"))
        if dosya_ismi:
            img1 = cv2.imread(dosya_ismi[0], cv2.IMREAD_COLOR)
            global row_inp, column_inp, channel_inp
            row_inp, column_inp, channel_inp = img1.shape
            row = row_inp
            column = column_inp
            # cevirmeden
            global histogramArray_input
            for i in range(0, row):
                for j in range(0, column):
                    histogramArray_input[0, img1[i, j, 0]] += 1  # blue
                    histogramArray_input[1, img1[i, j, 1]] += 1  # green
                    histogramArray_input[2, img1[i, j, 2]] += 1  # red
            '''
            pixmap = QtGui.QPixmap(dosya_ismi)
            pixmap = pixmap.scaled(self.image_i.width(), self.image_i.height(), QtCore.Qt.KeepAspectRatio)
            self.image_i.setPixmap(pixmap)
            self.image_i.setAlignment(QtCore.Qt.AlignCenter)
            '''
            # print(histogramArray_input)
            # plt.plot(histogramArray_input[0],color='blue')
            # plt.plot(histogramArray_input[1], color='green')
            # plt.plot(histogramArray_input[2], color='red')
            # plt.show()
            img_new = img1
            self.draw_figures(img1, histogramArray_input)
            print("Open Inputa basıldı.")

    def open_target_file(self):
        dosya_ismi = QFileDialog.getOpenFileName(self, "Dosya Aç", os.getenv("HOME"))
        if dosya_ismi:

            img2 = cv2.imread(dosya_ismi[0], cv2.IMREAD_COLOR)
            global row_target, column_target, channel_target
            row_target, column_target, channel_target = img2.shape
            row = row_target
            column = column_target
            # cevirmeden
            global histogramArray_target
            sizes = (3, 256)
            histogramArray = np.zeros(sizes)  # for bgr
            for i in range(0, row):
                for j in range(0, column):
                    histogramArray_target[0, img2[i, j, 0]] += 1  # blue
                    histogramArray_target[1, img2[i, j, 1]] += 1  # green
                    histogramArray_target[2, img2[i, j, 2]] += 1  # red
            # plt.plot(histogramArray_target[0],color='blue')
            # plt.plot(histogramArray_target[1], color='green')
            # plt.plot(histogramArray_target[2], color='red')
            #    plt.show()
            self.draw_figures(img2, histogramArray_target)
            print("Open Target File basıldı.")

    def save_file(self):
        print("Save File basıldı.")

    def equalize_photos(self):
        global histogramArray_result, row_inp, column_inp, row_target, column_target
        temp_input = deepcopy(histogramArray_input)
        temp_target = deepcopy(histogramArray_target)
        # cumulative and ratio

        temp_input = self.take_cumulative(temp_input)
        temp_input = self.take_ratio(temp_input, row_inp, column_inp)
        temp_target = self.take_cumulative(temp_target)
        temp_target = self.take_ratio(temp_target, row_target, column_target)
        # LOOK UP TABLE
        lut = self.create_lut(temp_input, temp_target)

        new_image = np.zeros((row_inp, column_inp, 3))

        print(row_inp)
        print(column_inp)
        for i in range(0, row_inp):
            for j in range(0, column_inp):
                new_image[i, j, 0] = int(lut[0, int(img_new[i, j, 0])])
                new_image[i, j, 1] = int(lut[1, int(img_new[i, j, 1])])
                new_image[i, j, 2] = int(lut[2, int(img_new[i, j, 2])])

        k = np.uint8(new_image)

        for i in range(0, row_inp):
            for j in range(0, column_inp):
                histogramArray_result[0, int(new_image[i, j, 0])] += 1  # blue
                histogramArray_result[1, int(new_image[i, j, 1])] += 1  # green
                histogramArray_result[2, int(new_image[i, j, 2])] += 1  # red

        self.draw_figures(k, histogramArray_result)

        '''

        '''
        print("Equalizea basıldı.")

    def take_cumulative(self, arr):
        for i in range(1, 256):
            arr[0, i] += arr[0, i - 1]
            arr[1, i] += arr[1, i - 1]
            arr[2, i] += arr[2, i - 1]
        return arr

    def take_ratio(self, arr, r, c):
        for x in range(0, 256):
            arr[0, x] = arr[0, x] / (r * c)
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

    def draw_figures(self, img, hist):

        plt.subplot(4, 1, 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.subplot(4, 1, 2)
        plt.plot(hist[0], color='blue')
        plt.subplot(4, 1, 3)
        plt.plot(hist[1], color='green')
        plt.subplot(4, 1, 4)
        plt.plot(hist[2], color='red')
        '''
        canvas = FigureCanvas()
        canvas.move(0,0)
        fig = Figure(figsize=(4, 5), dpi=100)
        canvas.axes = fig.add_subplot(plt)
        canvas.__init__(self,fig)
        x = np.array([50,30,40])
        labels = ["input", "target", "result"]
        ax = canvas.figure.add_subplot(111)
        ax.pie(x, labels = labels)
        '''
        plt.show()

class Canvas(FigureCanvas):
    def __init__(self, parent = None,  dpi =100):
        fig = Figure(figsize=(4, 5), dpi = dpi)
        self.axes = fig.add_subplot(f)

        FigureCanvas.__init__(self,fig)
        self.setParent(parent)
        self.plot()
    def plot(self):
        x = np.array([50,30,40])
        labels = ["input", "target", "result"]
        ax = self.figure.add_subplot(111)
        ax.pie(x, labels = labels)

class Menu(QMainWindow):

    def __init__(self):
        super().__init__()

        self.window = Histogram()
        self.setCentralWidget(self.window)

        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()

        file = menubar.addMenu("File")

        # Menude alt komutlar-ACTIONS- ekleme islemi
        open_source_file = QAction("Open Input File", self)
        open_source_file.setShortcut("Ctrl+I")

        open_target_file = QAction("Open Target File", self)
        open_target_file.setShortcut("Ctrl+T")

        save_file = QAction("Save File", self)
        save_file.setShortcut("Ctrl+S")

        exit_fromApp = QAction("Exit", self)
        exit_fromApp.setShortcut("ESC")

        # actionlari menuye ekleme islemi
        file.addAction(open_source_file)
        file.addAction(open_target_file)
        file.addAction(save_file)
        file.addAction(exit_fromApp)

        file.triggered.connect(self.response)

        self.setWindowTitle("Histogram Application by Alparslan Kivrak")
        self.show()

    def response(self, action):

        if action.text() == "Open Input File":
            self.window.open_input_file()
        elif action.text() == "Open Target File":
            self.window.open_target_file()
        elif action.text() == "Save File":
            self.window.save_file()
        elif action.text() == "Exit":
            print("Exita basıldı.")
            qApp.quit()


app = QApplication(sys.argv)

menu = Menu()

sys.exit(app.exec_())
