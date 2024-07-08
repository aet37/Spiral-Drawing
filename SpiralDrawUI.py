from Accelerometer import *
from PaintFunctions import *
import os
import sys

if sys.platform == 'win32':
	import warnings
	warnings.simplefilter("ignore", UserWarning)
	sys.coinit_flags = 2
	#import pywinauto

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from datetime import datetime

# UI Setup
app = QtWidgets.QApplication(sys.argv)

class spiralDrawSystem(QtWidgets.QMainWindow):

	# UI Class initializer / LOAD THE UI
	def __init__(self):
		super(spiralDrawSystem, self).__init__()
		if sys.platform == 'win32':
			uic.loadUi('spiralDraw_win.ui', self)
		else:
			uic.loadUi('spiralDraw.ui', self)
		self.move(0, 0)


		self.setWindowTitle("HIFU Spiral Drawing")

		###########################################################################################
		## Class Variables
		###########################################################################################

		# Case Setup variables
		if sys.platform == 'win32':
			print('Windows Detected')
			self.basePath = 'C:/hifu/HIFU-cases/'

		else:
			tmpdir = os.getcwd()
			tmpdir = tmpdir.split('/')
			self.basePath = '/' + tmpdir[1] + '/'+ tmpdir[2] + '/HIFU-cases/'

		# If the base directory doesnt exist, make it
		if not os.path.exists(self.basePath):
			os.mkdir(self.basePath)

		self.pt_id = ''
		self.data_save_path = ''
		self.current_trial = ''
		self.first_download = True
		self.prev_pt_lists = next(os.walk(self.basePath))[1]
		self.accel_files = []
		self.intraop_current = 1

		# Acclerometer
		self.accel_address = 'C5:02:6A:76:E4:5D'
		self.accelDevice = Accelerometer(self.accel_address)

		# Spiral
		self.previous_spiral_ccw = ''
		self.previous_spiral_cw = ''
		self.previous_spiral_line = ''

		# New or loaded case flag
		self.isNewCase = False

		###########################################################################################
		## Buttons / Screen Items
		###########################################################################################

		# Group Boxes
		self.trialNameSelect = self.findChild(QtWidgets.QGroupBox, 'accel_trial_sel')

		# Line Edits
		self.patientIdEnter = self.findChild(QtWidgets.QLineEdit, 'patientIdEnter')
		self.trialNameAccelerom = self.findChild(QtWidgets.QLineEdit, 'trialNameAccel')

		# Spin box
		self.intraopValueFeild = self.findChild(QtWidgets.QSpinBox, 'intraopValue')

		# Push Buttons
		self.startCaseButton = self.findChild(QtWidgets.QPushButton, 'startCase')
		self.startCaseButton.clicked.connect(self.start_case)
		self.stopCaseButton = self.findChild(QtWidgets.QPushButton, 'finishCaseButton')
		self.stopCaseButton.clicked.connect(self.finish_case)
		self.loadCaseButton = self.findChild(QtWidgets.QPushButton, 'loadCaseButton')
		self.loadCaseButton.clicked.connect(self.load_case)
		self.resetBoardButton = self.findChild(QtWidgets.QPushButton, 'resetBoard')
		self.resetBoardButton.clicked.connect(self.handle_reset)

		self.recordAccelButton = self.findChild(QtWidgets.QPushButton, 'recordAccel')
		self.recordAccelButton.clicked.connect(self.record_accel)
		self.downloadAccelButton = self.findChild(QtWidgets.QPushButton, 'downloadAccel')
		self.downloadAccelButton.clicked.connect(self.download_accel)
		self.cancelRecordButton = self.findChild(QtWidgets.QPushButton, 'cancelRecord')
		self.cancelRecordButton.clicked.connect(self.cancel_accel_record)

		# Radio Button
		self.preopRadioButton = self.findChild(QtWidgets.QRadioButton, 'preopRadio')
		self.intraopRadioButton = self.findChild(QtWidgets.QRadioButton, 'intraopRadio')
		self.postopRadioButton = self.findChild(QtWidgets.QRadioButton, 'postopRadio')
		self.otherRadioButton = self.findChild(QtWidgets.QRadioButton, 'otherRadio')
		self.testRadioButton = self.findChild(QtWidgets.QRadioButton, 'testRadio')
		self.penRadioButton = self.findChild(QtWidgets.QRadioButton, 'penRadio')
		self.tabletRadioButton = self.findChild(QtWidgets.QRadioButton, 'tabletRadio')

		# Tab Widgets
		self.aboutCaseWindow = self.findChild(QtWidgets.QWidget, 'aboutCase')
		self.accelControlWindow = self.findChild(QtWidgets.QWidget, 'accelControl')
		self.spiralControlWindow = self.findChild(QtWidgets.QWidget, 'spiralControl')

		# Drawing Area and Buttons for Spiral Drawing Tab
		self.SpiralCCWArea = self.findChild(QtWidgets.QLabel, 'spiral_ccw_draw')
		self.SpiralCWArea = self.findChild(QtWidgets.QLabel, 'spiral_cw_draw')
		self.SpiralLineArea = self.findChild(QtWidgets.QLabel, 'line_draw')

		# Create instances of DrawingLabel
		self.drawingAreaCCW = DrawingArea('ims/spiral_ccw_big.png', self.SpiralCCWArea.parent())
		self.drawingAreaCW = DrawingArea('ims/spiral_cw_big.png', self.SpiralCWArea.parent())
		self.drawingAreaLine = DrawingArea('ims/line.png', self.SpiralLineArea.parent())

		# Set the new DrawingLabel instances to have the same geometry as the original labels
		self.drawingAreaCCW.setGeometry(self.SpiralCCWArea.geometry())
		self.drawingAreaCW.setGeometry(self.SpiralCWArea.geometry())
		self.drawingAreaLine.setGeometry(self.SpiralLineArea.geometry())

		self.drawingAreaCCW.show()
		self.drawingAreaCW.show()
		self.drawingAreaLine.show()

		self.SpiralCCWArea.hide()
		self.SpiralCWArea.hide()
		self.SpiralLineArea.hide()

		# Set background images for the drawing areas
		self.drawingAreaCCW.setImage()
		self.drawingAreaCW.setImage()
		self.drawingAreaLine.setImage()

		# Ensure the original labels are visible (if needed)
		self.SpiralCCWArea.setVisible(True)
		self.SpiralCWArea.setVisible(True)
		self.SpiralLineArea.setVisible(True)

		# Add functionality to buttons
		self.doneCCWButton = self.findChild(QtWidgets.QPushButton, 'done_ccw_button')
		self.doneCCWButton.clicked.connect(self.onDoneCCW)
		self.doneCWButton = self.findChild(QtWidgets.QPushButton, 'done_cw_button')
		self.doneCWButton.clicked.connect(self.onDoneCW)
		self.doneLineButton = self.findChild(QtWidgets.QPushButton, 'done_line_button')
		self.doneLineButton.clicked.connect(self.onDoneLine)

		self.LoadPrevCCWButton = self.findChild(QtWidgets.QPushButton, 'loadp_spiralccw_button')
		self.LoadPrevCCWButton.clicked.connect(self.onLoadPreviousCCW)
		self.LoadPrevCWButton = self.findChild(QtWidgets.QPushButton, 'loadp_spiralcw_button')
		self.LoadPrevCWButton.clicked.connect(self.onLoadPreviousCW)
		self.LoadPrevLineButton = self.findChild(QtWidgets.QPushButton, 'loadp_line_button')
		self.LoadPrevLineButton.clicked.connect(self.onLoadPreviousLine)

		self.ClearDrawingsButton = self.findChild(QtWidgets.QPushButton, 'clear_drawings')
		self.ClearDrawingsButton2 = self.findChild(QtWidgets.QPushButton, 'clear_drawings2')
		self.ClearDrawingsButton.clicked.connect(self.onClearDrawings)
		self.ClearDrawingsButton2.clicked.connect(self.onClearDrawings)

		# Line edits
		self.accelDeviceUpdates = self.findChild(QtWidgets.QLabel, 'accelDeviceUpdate')

		# List Widgets
		self.patientList = self.findChild(QtWidgets.QListView, 'prevPatientList')
		self.accelCasesList = self.findChild(QtWidgets.QListView, 'accelCases')

		# Add all previous cases in the QListView Object
		for item in self.prev_pt_lists:
			self.patientList.addItem(item)

		self.show()

	###############################################################################################
	## Helper Functions
	###############################################################################################



	###############################################################################################
	## Button Click Functions
	###############################################################################################

	# Function to start the case
	def start_case(self):

		# Get the patient ID, remove all sapces from the ID
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

	# Function to finish the case
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

		# Clear the accleration list cases
		self.accelCasesList.clear()

		# Write a txt file that stores the case
		self.pt_id = ''
		self.data_save_path = ''
		self.accel_files = []
		self.isNewCase = False

	# Function to load a previous case
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
		self.resetBoardButton.setEnabled(False)

		# Add any accel trials to the case
		for item in self.accel_files:
			self.accelCasesList.addItem(item)


	# Function to start the accelerometer recording
	def record_accel(self):

		if self.preopRadioButton.isChecked():
			tmp_str = 'preop'

		elif self.intraopRadioButton.isChecked():
			tmp_str = 'intraop' + str(self.intraop_current)

		elif self.postopRadioButton.isChecked():
			tmp_str = 'postop'

		elif self.otherRadioButton.isChecked():
			# Check that two trials are not named the same
			tmp_str = self.trialNameAccelerom.text()
			tmp_str.replace(' ', '')

		elif self.testRadioButton.isChecked():
			tmp_str = 'test'
		else:
			tmp_str = ''

		if tmp_str == '' or (tmp_str in self.accel_files):
			return
		else:
			self.current_trial = tmp_str

		# Set the proper BT address
		if self.penRadioButton.isChecked():
			self.accel_address = 'C5:02:6A:76:E4:5D'
		elif self.tabletRadioButton.isChecked():
			self.accel_address = 'DA:83:E6:EE:AB:BF'
		else:
			self.accel_address = 'C5:02:6A:76:E4:5D'

		# Disable the record button
		self.recordAccelButton.setEnabled(False)

		# Update user thatdevice is being set up
		self.accelDeviceUpdates.setText('Connecting to device ...')
		self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()


		self.accelDevice = Accelerometer(self.accel_address, self.basePath + self.pt_id + '/' + self.current_trial + '.csv')

		# Establish connection
		connected = False
		for i in range(1):
			connected = self.accelDevice.connect()
			if connected:
				break
			else:
				self.accelDeviceUpdates.setText('Still connecting ...')
				self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

				#Force GUI to update (needed due to many sleep() calls associated with BT device)
				app.processEvents()

				print('Trying to establish connection again...')
				sleep(1)

		if not connected:
			# Update user that device is being set up
			self.accelDeviceUpdates.setText('Could not connect. Try again.')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			# Enable the record button
			self.recordAccelButton.setEnabled(True)

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()
			return

		# Update user that device is being set up
		self.accelDeviceUpdates.setText('Connected. Setting up device ...')
		self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()

		isRecording = self.accelDevice.log()
		if isRecording:
			self.accelDeviceUpdates.setText('Recording ...')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			# Save file name and disable record button (only allow download)
			self.trialNameAccelerom.setEnabled(False)
			self.recordAccelButton.setEnabled(False)
			self.downloadAccelButton.setEnabled(True)
			self.cancelRecordButton.setEnabled(True)
			self.trialNameSelect.setEnabled(False)
		else:
			# Enable the record button again
			self.recordAccelButton.setEnabled(True)
			print('Error in BT setup... try again')

	# Fuction to download the acclerometer recording after spiral is done
	def download_accel(self):

		# Check to make sure device did not loose connection
		if self.accelDevice.isConnected:
			print('Downloading data...')

			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Downloading data ...')
			self.accelDeviceUpdates.setStyleSheet('Color: green;')

			# Disable Download and cancel buttons
			self.downloadAccelButton.setEnabled(False)
			self.cancelRecordButton.setEnabled(False)

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			#isDownloaded = self.accelDevice.stop_log(self.data_save_path + self.current_trial + '.csv')
			isDownloaded = self.accelDevice.stop_log()
		else:
			print('Connecton lost during recording... Trying to reestablish...')

			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Reconnecting ...')
			self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			connected = False
			for i in range(2):
				connected = self.accelDevice.connect()
				if connected:
					break
				else:
					print('Trying to establish connection again...')
					sleep(1)

			# After connection, call is_downloaded function
			if self.accelDevice.isConnected:
				print('Downloading...')

				# Signal to UI that the data is being downloaded
				self.accelDeviceUpdates.setText('Downloading data ...')
				self.accelDeviceUpdates.setStyleSheet('Color: green;')

				#Force GUI to update (needed due to many sleep() calls associated with BT device)
				app.processEvents()

				#isDownloaded = self.accelDevice.stop_log(self.data_save_path + self.current_trial + '.csv')
				isDownloaded = self.accelDevice.stop_log()
			else:
				isDownloaded = False

				# Signal to UI that the data is being downloaded
				self.accelDeviceUpdates.setText('Connect failed. Try again.')
				self.accelDeviceUpdates.setStyleSheet('Color: red;')

				#Force GUI to update (needed due to many sleep() calls associated with BT device)
				app.processEvents()

				print('  Could not download. Try again.')

		if isDownloaded:
			# Signal that downloading is complete
			print('  Done')

			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Done. Reseting BT ...')
			self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			# Get the accelerometer data and write it to file
			if self.current_trial != 'test':
				fl = open(self.basePath + self.pt_id + '.txt', 'a')
				fl.write(self.current_trial + '\n')
				fl.close()

			# Disable buttons and add trial to list
			if self.current_trial != 'test':
				self.accelCasesList.addItem(self.current_trial)
				self.accel_files.append(self.current_trial)
			self.trialNameAccelerom.setEnabled(True)
			self.recordAccelButton.setEnabled(True)
			self.downloadAccelButton.setEnabled(False)
			self.cancelRecordButton.setEnabled(False)
			self.trialNameSelect.setEnabled(True)
			if self.intraopRadioButton.isChecked():
				self.intraop_current += 1
				self.intraopValueFeild.setValue(self.intraop_current)
			self.current_trial = ''

			print('Reseting ...')
			self.accelDevice.reset()

			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Done. Ready for next trial.')
			self.accelDeviceUpdates.setStyleSheet('Color: green;')

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			print('. Done.... Ready for next trial')
		else:
			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Download failed. Try again.')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			# Disable Download and cancel buttons
			self.downloadAccelButton.setEnabled(True)
			self.cancelRecordButton.setEnabled(True)

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			print('Error in downloading ... try again')

	# Function to cancel the accelerometer recording button
	def cancel_accel_record(self):

		# Signal to UI that the data is being downloaded
		self.accelDeviceUpdates.setText('Cancel and Reset...')
		self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

		# Disable Download and cancel buttons
		self.downloadAccelButton.setEnabled(False)
		self.cancelRecordButton.setEnabled(False)

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()

		isCanceled = self.accelDevice.cancel_record()

		if isCanceled:
			# Disable buttons and add trial to list
			self.trialNameAccelerom.setEnabled(True)
			self.recordAccelButton.setEnabled(True)
			self.downloadAccelButton.setEnabled(False)
			self.cancelRecordButton.setEnabled(False)

			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Done. Ready for next trial.')
			self.accelDeviceUpdates.setStyleSheet('Color: green;')

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			self.current_trial = ''
			print('Canceled')
		else:
			# Signal to UI that the data is being downloaded
			self.accelDeviceUpdates.setText('Error in Cancel. Try again.')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()

			print('Could not cancel. Try again.')

		return

	# Function to handle reset request from user
	def handle_reset(self):
		print('Reseting BT board...')

		# Check to make sure device did not loose connection
		if self.accelDevice.isConnected:
			isReset = self.accelDevice.reset()
		else:
			print('Connecton lost ... Trying to reestablish...')
			connected = False
			for i in range(5):
				connected = self.accelDevice.connect()
				if connected:
					break
				else:
					print('Trying to establish connection again...')
					sleep(1)

			# After connection, call reset function
			if self.accelDevice.isConnected:
				print('Reseting BT board ...')
				isDownloaded = self.accelDevice.reset()
			else:
				isDownloaded = False
				print('  Could not download. Try again.')
	'''
	def onDone(self, id):
		if self.current_trial != '':
			file_path = self.basePath + self.pt_id + '/' + self.current_trial + '_' + id + '_spiral.csv'
		else:
			file_path = self.basePath + self.pt_id + '/' + id + '_spiral.csv'

		if id == 'ccw':
			self.drawingAreaCCW.saveDrawing(file_path)
			self.drawingAreaCCW.clearDrawing()
			self.previous_spiral_ccw = file_path
		elif id == 'cw':
			self.drawingAreaCW.saveDrawing(file_path)
			self.drawingAreaCW.clearDrawing()
			self.previous_spiral_cw = file_path
		elif id == 'line':
			self.drawingAreaLine.saveDrawing(file_path)
			self.drawingAreaLine.clearDrawing()
			self.previous_spiral_line = file_path
		else:
			print('Error... invalid id (check src code). Note: this is not a user problem, rather a code problem')
	'''

	def onDoneCCW(self):
		if self.current_trial != '':
			file_path = self.basePath + self.pt_id + '/' + self.current_trial + '_ccw_spiral.csv'
		else:
			file_path = self.basePath + self.pt_id + '/ccw_spiral.csv'

		self.drawingAreaCCW.saveDrawing(file_path)
		self.drawingAreaCCW.clearDrawing()
		self.previous_spiral_ccw = file_path

	def onDoneCW(self):
		if self.current_trial != '':
			file_path = self.basePath + self.pt_id + '/' + self.current_trial + '_cw_spiral.csv'
		else:
			file_path = self.basePath + self.pt_id + '/cw_spiral.csv'

		self.drawingAreaCW.saveDrawing(file_path)
		self.drawingAreaCW.clearDrawing()
		self.previous_spiral_cw = file_path

	def onDoneLine(self):
		if self.current_trial != '':
			file_path = self.basePath + self.pt_id + '/' + self.current_trial + '_line_spiral.csv'
		else:
			file_path = self.basePath + self.pt_id + '/line_spiral.csv'

		self.drawingAreaLine.saveDrawing(file_path)
		self.drawingAreaLine.clearDrawing()
		self.previous_spiral_line = file_path
	'''
	def onLoadPrevious(self, id):
		if id == 'ccw':
			if self.previous_spiral_ccw != '':
				self.drawingAreaCCW.loadDrawing(self.previous_spiral_ccw)
			else:
				return
		elif id == 'cw':
			if self.previous_spiral_cw != '':
				self.drawingAreaCW.loadDrawing(self.previous_spiral_cw)
			else:
				return
		elif id == 'line':
			if self.previous_spiral_line != '':
				self.drawingAreaLine.loadDrawing(self.previous_spiral_line)
			else:
				return
		else:
			print('Error... invalid id (check src code). Note: this is not a user problem, rather a code problem')
	'''

	def onLoadPreviousCCW(self):
		if self.previous_spiral_ccw != '':
			self.drawingAreaCCW.loadDrawing(self.previous_spiral_ccw)
		else:
			return

	def onLoadPreviousCW(self):
		if self.previous_spiral_cw != '':
			self.drawingAreaCW.loadDrawing(self.previous_spiral_cw)
		else:
			return

	def onLoadPreviousLine(self):
		if self.previous_spiral_line != '':
			self.drawingAreaLine.loadDrawing(self.previous_spiral_line)
		else:
			return

	def onClearDrawings(self):
		self.drawingAreaCCW.clearDrawing()
		self.drawingAreaCW.clearDrawing()
		self.drawingAreaLine.clearDrawing()

# Start UI
window = spiralDrawSystem()
if sys.platform != 'win32':
	os.system('clear')
app.exec_()

# To do before system Exit
if sys.platform != 'win32':
	os.system('clear')
