from Accelerometer import *
from SpiralWorkerClasses import *
import os
import sys
import threading

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
		uic.loadUi('spiralDraw_win.ui', self)
		self.move(0, 0)


		self.setWindowTitle("HIFU Spiral Drawing")

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
		self.recordAccelButton.clicked.connect(self.record_accel_thread)
		self.downloadAccelButton = self.findChild(QtWidgets.QPushButton, 'downloadAccel')
		self.downloadAccelButton.clicked.connect(self.download_accel_thread)
		self.cancelRecordButton = self.findChild(QtWidgets.QPushButton, 'cancelRecord')
		self.cancelRecordButton.clicked.connect(self.cancel_accel_thread)

		# Radio Button
		self.preopRadioButton = self.findChild(QtWidgets.QRadioButton, 'preopRadio')
		self.intraopRadioButton = self.findChild(QtWidgets.QRadioButton, 'intraopRadio')
		self.postopRadioButton = self.findChild(QtWidgets.QRadioButton, 'postopRadio')
		self.otherRadioButton = self.findChild(QtWidgets.QRadioButton, 'otherRadio')
		self.testRadioButton = self.findChild(QtWidgets.QRadioButton, 'testRadio')

		# Tab Widgets
		self.aboutCaseWindow = self.findChild(QtWidgets.QWidget, 'aboutCase')
		self.accelControlWindow = self.findChild(QtWidgets.QWidget, 'accelControl')
		self.spiralControlWindow = self.findChild(QtWidgets.QWidget, 'spiralControl')

		# Line edits
		self.accelDeviceUpdates = self.findChild(QtWidgets.QLabel, 'accelDeviceUpdate')

		# List Widgets
		self.patientList = self.findChild(QtWidgets.QListView, 'prevPatientList')
		self.accelCasesList = self.findChild(QtWidgets.QListView, 'accelCases')

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

		# New or loaded case flag
		self.isNewCase = False

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

	###############################################################################################
	## Worker threads
	###############################################################################################

	# Define threads for each of the 3 time consuming processes
	def record_accel_thread(self):
		print('Enter Record thread')
		t1 = threading.Thread(target=self.record_accel)
		t1.start()

	# Define threads for each of the 3 time consuming processes
	def download_accel_thread(self):
		print('Enter Download thread')
		t2 = threading.Thread(target=self.download_accel)
		t2.start()

	# Define threads for each of the 3 time consuming processes
	def cancel_accel_thread(self):
		print('Enter Cancel thread')
		t3 = threading.Thread(target=self.cancel_accel_record)
		t3.start()

	# Destroy recording thread once it is done
	def destroy_record_thread(self):
		self.record_thread.exit()
		time.sleep(0.2)
		self.record_worker.deleteLater()
		self.record_thread.deleteLater()

	###############################################################################################
	###############################################################################################

	###############################################################################################
	## GUI record accel update functions
	###############################################################################################

	def started_btn_update(self):
		# Enable the record button
		self.recordAccelButton.setEnabled(True)

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()

	def failedstart_btn_update(self):
		self.accelDeviceUpdates.setText('Recording ...')
		self.accelDeviceUpdates.setStyleSheet('Color: red;')

		# Save file name and disable record button (only allow download)
		self.trialNameAccelerom.setEnabled(False)
		self.recordAccelButton.setEnabled(False)
		self.downloadAccelButton.setEnabled(True)
		self.cancelRecordButton.setEnabled(True)
		self.trialNameSelect.setEnabled(False)

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()

	###############################################################################################
	###############################################################################################

	# Function to start the accelerometer recording
	def record_accel(self):
		print('Record Clicked')

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

		# Disable the record button
		self.recordAccelButton.setEnabled(False)

		# Update user thatdevice is being set up
		self.accelDeviceUpdates.setText('Connecting to device ...')
		self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

		print('Connecting...')

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()


		self.accelDevice = Accelerometer(self.accel_address, self.basePath + self.pt_id + '/' + self.current_trial + '.csv')

		# Start Thread
		self.record_thread = QThread()

		# Initialize worker
		self.record_worker = RecordWorker(self.accelDevice)

		# Move the worker to the thread
		self.record_worker.moveToThread(self.record_thread)

		# Connect Worker signals
		self.record_thread.started.connect(self.record_worker.run)
		self.record_worker.finished.connect(self.destroy_record_thread)

		# Connect UI update signals
		self.record_worker.sucessStart.connect(self.started_btn_update)
		self.record_worker.failedStart.connect(self.failedstart_btn_update)

		# Start the thread
		self.record_thread.start()


		'''
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
			return
		else:
			# Enable the record button again
			self.recordAccelButton.setEnabled(True)
			print('Error in BT setup... try again')
			return
		'''

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

# Start UI
window = spiralDrawSystem()
if sys.platform != 'win32':
	os.system('clear')
app.exec_()

# To do before system Exit
if sys.platform != 'win32':
	os.system('clear')
