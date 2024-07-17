import sys
import os
import csv
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class DrawingArea(QWidget):
    def __init__(self, parent=None):
        super(DrawingArea, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.drawing = False
        self.myPenWidth = 2
        self.myPenColor = Qt.blue

        # Load the background image
        self.background_image = QImage('spiral_temp_ccw.png')
        self.image = QPixmap(self.size())
        self.image.fill(Qt.white)

        self.lastPoint = QPoint()
        self.drawn_points = []  # To store the time and coordinates of drawn points

    def resizeEvent(self, event):
        # Scale the background image to fit the widget size
        scaled_background = self.background_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image = QPixmap(self.size())
        self.image.fill(Qt.white)

        # Center the scaled background image
        painter = QPainter(self.image)
        offset_x = (self.width() - scaled_background.width()) // 2
        offset_y = (self.height() - scaled_background.height()) // 2
        painter.drawImage(offset_x, offset_y, scaled_background)
        painter.end()

        self.update()

    def resizeWin(self):
        # Scale the background image to fit the widget size
        scaled_background = self.background_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image = QPixmap(self.size())
        self.image.fill(Qt.white)

        # Center the scaled background image
        painter = QPainter(self.image)
        offset_x = (self.width() - scaled_background.width()) // 2
        offset_y = (self.height() - scaled_background.height()) // 2
        painter.drawImage(offset_x, offset_y, scaled_background)
        painter.end()

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            currentPoint = event.pos()
            currentTime = datetime.now()
            self.drawn_points.append((currentTime, currentPoint.x(), currentPoint.y()))

            painter = QPainter(self.image)
            pen = QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.lastPoint, currentPoint)
            self.lastPoint = currentPoint
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            currentPoint = event.pos()
            currentTime = datetime.now()
            self.drawn_points.append((currentTime, currentPoint.x(), currentPoint.y()))

            painter = QPainter(self.image)
            pen = QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.lastPoint, currentPoint)
            self.drawing = False
            self.update()

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawPixmap(self.rect(), self.image)

    def clearDrawing(self):
        self.image.fill(Qt.white)
        painter = QPainter(self.image)
        offset_x = (self.width() - self.background_image.width()) // 2
        offset_y = (self.height() - self.background_image.height()) // 2
        painter.drawImage(offset_x, offset_y, self.background_image)
        painter.end()
        self.drawn_points = []
        self.resizeWin()
        self.update()

    def saveDrawing(self, file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'X', 'Y'])
            for point in self.drawn_points:
                writer.writerow([point[0].strftime("%Y-%m-%d %H:%M:%S.%f"), point[1], point[2]])

    def loadDrawing(self, file_path):
        self.clearDrawing()
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                self.drawn_points = []
                previousPoint = None
                for row in reader:
                    time_str, x, y = row
                    point = QPoint(int(x), int(y))
                    currentTime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                    self.drawn_points.append((currentTime, point.x(), point.y()))

                    if previousPoint is not None:
                        painter = QPainter(self.image)
                        pen = QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                        painter.setPen(pen)
                        painter.drawLine(previousPoint, point)
                        painter.end()

                    previousPoint = point
            self.update()
        except Exception as e:
            print(f"Error loading drawing: {e}")

class spiralDrawSystem(QtWidgets.QMainWindow):

    # UI Class initializer / LOAD THE UI
    def __init__(self):
        super(spiralDrawSystem, self).__init__()
        uic.loadUi('spiralDraw.ui', self)
        self.move(0, 0)

        self.setWindowTitle("HIFU Spiral Drawing")

        ###########################################################################################
        ## Buttons / Screen Items
        ###########################################################################################

        # Line Edits
        self.patientIdEnter = self.findChild(QtWidgets.QLineEdit, 'patientIdEnter')
        self.trialNameAccelerom = self.findChild(QtWidgets.QLineEdit, 'trialNameAccel')

        # Push Buttons
        self.startCaseButton = self.findChild(QtWidgets.QPushButton, 'startCase')
        self.startCaseButton.clicked.connect(self.start_case)
        self.stopCaseButton = self.findChild(QtWidgets.QPushButton, 'finishCaseButton')
        self.stopCaseButton.clicked.connect(self.finish_case)
        self.loadCaseButton = self.findChild(QtWidgets.QPushButton, 'loadCaseButton')
        self.loadCaseButton.clicked.connect(self.load_case)

        self.recordAccelButton = self.findChild(QtWidgets.QPushButton, 'recordAccel')
        self.recordAccelButton.clicked.connect(self.record_accel)
        self.downloadAccelButton = self.findChild(QtWidgets.QPushButton, 'downloadAccel')
        self.downloadAccelButton.clicked.connect(self.download_accel)
        self.cancelRecordButton = self.findChild(QtWidgets.QPushButton, 'cancelRecord')
        self.cancelRecordButton.clicked.connect(self.cancel_accel_record)

        # Tab Widgets
        self.tabWidget = self.findChild(QTabWidget, 'CaseViewer')
        if self.tabWidget is None:
            raise ValueError("Tab widget not found. Please check the object name in the UI file.")

        self.aboutCaseWindow = self.findChild(QtWidgets.QWidget, 'aboutCase')
        self.accelControlWindow = self.findChild(QtWidgets.QWidget, 'accelControl')
        self.spiralControlWindow = self.findChild(QtWidgets.QWidget, 'spiralControl')

        # Drawing Area and Buttons for Spiral Drawing Tab
        self.drawingArea = DrawingArea(self.spiralControlWindow)
        self.doneButton = QtWidgets.QPushButton("Done", self.spiralControlWindow)
        self.loadButton = QtWidgets.QPushButton("Load Previous", self.spiralControlWindow)

        # Set up layout for the drawing area and buttons
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.drawingArea)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.doneButton)
        self.buttonLayout.addWidget(self.loadButton)

        self.layout.addLayout(self.buttonLayout)
        self.spiralControlWindow.setLayout(self.layout)

        self.doneButton.clicked.connect(self.onDone)
        self.loadButton.clicked.connect(self.onLoadPrevious)

        # Save the Base Directory
        tmpdir = os.getcwd().partition('Spiral-Drawing')
        self.basePath = tmpdir[0] + tmpdir[1] + '/' + tmpdir[2] + '/HIFU-cases/'

        # If the base directory doesn't exist, make it
        if not os.path.exists(self.basePath):
            os.mkdir(self.basePath)

        self.pt_id = ''
        self.data_save_path = ''
        self.current_trial = ''
        self.prev_pt_lists = next(os.walk(self.basePath))[1]
        self.accel_files = []

        # New or loaded case flag
        self.isNewCase = False

        # Add all previous cases in the QListView Object
        self.patientList = self.findChild(QtWidgets.QListWidget, 'patientList')
        for item in self.prev_pt_lists:
            self.patientList.addItem(item)

        # Add a new tab for the plot
        self.viewProgressTab = QWidget()
        self.viewProgressLayout = QVBoxLayout(self.viewProgressTab)
        self.tabWidget.addTab(self.viewProgressTab, "View Progress")
        self.plotButton = QtWidgets.QPushButton("Plot y = x^2", self.viewProgressTab)
        self.viewProgressLayout.addWidget(self.plotButton)
        self.plotButton.clicked.connect(self.plot_graph)

        self.show()

    ###############################################################################################
    ## Button Click Functions
    ###############################################################################################

    def start_case(self):
        # Get the patient ID, remove all spaces from the ID
        tmp_ptid= self.patientIdEnter.text()
        tmp_ptid.replace(' ', '')
        self.prev_pt_list = next(os.walk(self.basePath))[1]

        if tmp_ptid == '' or (tmp_ptid in self.prev_pt_list):
            return
        else:
            self.aboutCaseWindow.setEnabled(True)
            self.accelControlWindow.setEnabled(True)
            self.spiralControlWindow.setEnabled(True)
            self.startCaseButton.setEnabled(False)
            self.stopCaseButton.setEnabled(True)
            self.loadCaseButton.setEnabled(False)
            self.patientIdEnter.setEnabled(False)
            self.trialNameAccelerom.setEnabled(True)
            self.downloadAccelButton.setEnabled(False)
            self.cancelRecordButton.setEnabled(False)

            self.isNewCase = True

            # Write a txt file that stores the case
            self.pt_id = tmp_ptid
            fl = open(self.basePath + self.pt_id + '.txt', 'w')
            fl.write(self.pt_id + '\n' + self.basePath + self.pt_id + '/' + '\n' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '\n\n')
            fl.close()
            self.data_save_path = self.basePath + self.pt_id + '/'
            os.mkdir(self.data_save_path)

    def finish_case(self):
        self.aboutCaseWindow.setEnabled(False)
        self.accelControlWindow.setEnabled(False)
        self.spiralControlWindow.setEnabled(False)
        self.startCaseButton.setEnabled(True)
        self.stopCaseButton.setEnabled(False)
        self.loadCaseButton.setEnabled(True)
        self.patientIdEnter.setEnabled(True)
        self.patientIdEnter.setText('')
        self.trialNameAccelerom.setText('')

        # Add all previous cases in the QListView Object
        self.prev_pt_list = next(os.walk(self.basePath))[1]

        if self.isNewCase:
            self.patientList.addItem(self.pt_id)

        # Clear the acceleration list cases
        self.accelCasesList = self.findChild(QtWidgets.QListWidget, 'accelCasesList')
        self.accelCasesList.clear()

        # Write a txt file that stores the case
        self.pt_id = ''
        self.data_save_path = ''
        self.accel_files = []
        self.isNewCase = False

    def load_case(self):
        # Load the patient ID, and set the class variables
        self.pt_id = self.patientList.currentItem().text()
        self.data_save_path = self.basePath + self.pt_id + '/'
        self.patientIdEnter.setText(self.pt_id)

        self.accel_files = []
        with open(self.basePath + self.pt_id + '.txt') as file:
            for line in file:
                self.accel_files.append(line.rstrip())

        del(self.accel_files[0])
        del(self.accel_files[0])
        del(self.accel_files[0])
        del(self.accel_files[0])

        # Disable all other start case functions
        self.aboutCaseWindow.setEnabled(True)
        self.accelControlWindow.setEnabled(True)
        self.spiralControlWindow.setEnabled(True)
        self.startCaseButton.setEnabled(False)
        self.stopCaseButton.setEnabled(True)
        self.loadCaseButton.setEnabled(False)
        self.patientIdEnter.setEnabled(False)
        self.trialNameAccelerom.setEnabled(True)
        self.downloadAccelButton.setEnabled(False)
        self.cancelRecordButton.setEnabled(False)

        # Add any accel trials to the case
        self.accelCasesList = self.findChild(QtWidgets.QListWidget, 'accelCasesList')
        for item in self.accel_files:
            self.accelCasesList.addItem(item)

    def record_accel(self):
        # Check that two trials are not named the same
        tmp_str = self.trialNameAccelerom.text()
        tmp_str.replace(' ', '')
        if tmp_str == '' or (tmp_str in self.accel_files):
            return
        else:
            self.current_trial = tmp_str

        # Save file name and disable record button (only allow download)
        self.trialNameAccelerom.setEnabled(False)
        self.recordAccelButton.setEnabled(False)
        self.downloadAccelButton.setEnabled(True)
        self.cancelRecordButton.setEnabled(True)

    def download_accel(self):
        # Get the accelerometer data and write it to file
        fl = open(self.basePath + self.pt_id + '.txt', 'a')
        fl.write(self.current_trial + '\n')
        fl.close()

        # Add accel filename to case file
        fl = open(self.basePath + self.pt_id + '/' + self.current_trial + '.txt', 'w')
        fl.write('Accel data written')
        fl.close()

        # Add to the list view
        self.accelCasesList.addItem(self.current_trial)

        # Disable buttons and add trial to list
        self.accel_files.append(self.current_trial)
        self.trialNameAccelerom.setEnabled(True)
        self.recordAccelButton.setEnabled(True)
        self.downloadAccelButton.setEnabled(False)
        self.cancelRecordButton.setEnabled(False)
        self.current_trial = ''

    def cancel_accel_record(self):
        # Disable buttons and add trial to list
        self.trialNameAccelerom.setEnabled(True)
        self.recordAccelButton.setEnabled(True)
        self.downloadAccelButton.setEnabled(False)
        self.cancelRecordButton.setEnabled(False)
        self.current_trial = ''

    def onDone(self):
        file_path = self.data_save_path + 'prev_drawing.csv'
        self.drawingArea.saveDrawing(file_path)
        self.drawingArea.clearDrawing()

    def onLoadPrevious(self):
        file_path = self.data_save_path + 'prev_drawing.csv'
        self.drawingArea.loadDrawing(file_path)

    def plot_graph(self):
        # Create a canvas for the plot
        sc = MplCanvas(self.viewProgressTab, width=5, height=4, dpi=100)
        t = np.linspace(-10, 10, 400)
        y = t**2
        sc.axes.plot(t, y)
        self.viewProgressLayout.addWidget(sc)
        sc.draw()

# UI Setup
app = QtWidgets.QApplication(sys.argv)

# Start UI
window = spiralDrawSystem()
os.system('clear')
app.exec_()

# To do before system Exit
os.system('clear')
