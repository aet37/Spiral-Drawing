from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time


class RecordWorker(QObject):

	# Signals to update UI
	finished = pyqtSignal()
	sucessStart = pyqtSignal()
	failedStart = pyqtSignal()


	def __init__(self, accel_object):
		QObject.__init__(self)
		self.accelDevice = accel_object

	def run(self):

		# Establish connection
		connected = False
		for i in range(1):
			connected = self.accelDevice.connect()
			if connected:
				break
			else:
				'''
				self.accelDeviceUpdates.setText('Still connecting ...')
				self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

				#Force GUI to update (needed due to many sleep() calls associated with BT device)
				app.processEvents()
				'''

				print('Trying to establish connection again...')
				sleep(1)

		if not connected:
			'''
			# Update user that device is being set up
			self.accelDeviceUpdates.setText('Could not connect. Try again.')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			# Enable the record button
			self.recordAccelButton.setEnabled(True)

			#Force GUI to update (needed due to many sleep() calls associated with BT device)
			app.processEvents()
			'''

			self.failedStart.emit()
			self.finished.emit()

			return

		'''
		# Update user that device is being set up
		self.accelDeviceUpdates.setText('Connected. Setting up device ...')
		self.accelDeviceUpdates.setStyleSheet('Color: yellow;')

		#Force GUI to update (needed due to many sleep() calls associated with BT device)
		app.processEvents()
		'''

		isRecording = self.accelDevice.log()
		if isRecording:
			'''
			self.accelDeviceUpdates.setText('Recording ...')
			self.accelDeviceUpdates.setStyleSheet('Color: red;')

			# Save file name and disable record button (only allow download)
			self.trialNameAccelerom.setEnabled(False)
			self.recordAccelButton.setEnabled(False)
			self.downloadAccelButton.setEnabled(True)
			self.cancelRecordButton.setEnabled(True)
			self.trialNameSelect.setEnabled(False)
			'''
			self.sucessStart.emit()
			print('Recording ...')
			self.finished.emit()
			return
		else:
			'''
			# Enable the record button again
			self.recordAccelButton.setEnabled(True)
			'''
			self.failedStart.emit()
			print('Error in BT setup... try again')
			self.finished.emit()
			return
