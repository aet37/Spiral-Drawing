from mbientlab.metawear import MetaWear, libmetawear, parse_value, create_voidp, create_voidp_int
from mbientlab.metawear.cbindings import *
from threading import Event
from time import sleep

class Accelerometer:

	# Setup function
	def __init__(self, address, fpath, fs=100):
		self.address = address
		self.fs = fs
		self.device = MetaWear(address)
		self.signal = []
		self.logger = []

		# Make the file to print out to
		self.f = open(fpath, 'w+')
		self.f.truncate()

		# Parsing + logging variables
		self.firstParse = True
		self.time_original = 0
		self.time_data = []
		self.data_x = []
		self.data_y = []
		self.data_z = []

	# Function to connect
	def connect(self):
		self.device.connect()
		return True

	# Start logging the acceleration
	def log(self):
		try:
			# Configure the board with the right frequency and g
			libmetawear.mbl_mw_acc_set_odr(self.device.board, self.fs)	# Start the accelerometer
			libmetawear.mbl_mw_acc_set_range(self.device.board, 16)	# Set range to +/-16g or closest valid range
			libmetawear.mbl_mw_acc_write_acceleration_config(self.device.board)

			# Start the logger
			self.signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(self.device.board)
			self.logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(self.signal, None, fn), resource = "acc_logger")
			libmetawear.mbl_mw_logging_start(self.device.board, 0)

			# Start the sampling
			libmetawear.mbl_mw_acc_enable_acceleration_sampling(self.device.board)
			libmetawear.mbl_mw_acc_start(self.device.board)

			return True # If run sucessful

		except RuntimeError as err:
			print(err)
			return False

	# Function to parse the data into a .csv file
	def parse(self, ctx, p):
		if self.firstParse:
			self.time_original = int(p.contents.epoch)
			self.firstParse = False

		self.f.write(str(int(p.contents.epoch) - self.time_original))
		self.time_data.append(p.contents.epoch - self.time_original)
		self.f.write(',')
		parsed_val = str(parse_value(p))
		parsed_val = parsed_val.replace('{', '')
		parsed_val = parsed_val.replace('}', '')
		parsed_val = parsed_val.replace(':', ',')
		parsed_val = parsed_val.replace(' ', '')
		parsed_val = parsed_val.split(',')

		self.data_x.append(float(parsed_val[1]))
		self.f.write(parsed_val[1])
		self.f.write(',')
		self.data_y.append(float(parsed_val[3]))
		self.f.write(parsed_val[3])
		self.f.write(',')
		self.data_z.append(float(parsed_val[5]))
		self.f.write(parsed_val[5])
		self.f.write('\n')

	# Stop logging and save to file
	def stop_log(self, fpath=''):
		try:
			# Setop acc
			libmetawear.mbl_mw_acc_stop(self.device.board)
			libmetawear.mbl_mw_acc_disable_acceleration_sampling(self.device.board)

			# Stop logging
			libmetawear.mbl_mw_logging_stop(self.device.board)

			# Flush cache if MMS
			libmetawear.mbl_mw_logging_flush_page(self.device.board)

			# Downloading data")
			libmetawear.mbl_mw_settings_set_connection_parameters(self.device.board, 7.5, 7.5, 0, 6000)
			sleep(1)

			# Setup Download handler
			e = Event()
			def progress_update_handler(context, entries_left, total_entries):
				if (entries_left == 0):
					e.set()

			fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
			download_handler = LogDownloadHandler(context = None, received_progress_update = fn_wrapper, received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))

			#callback = FnVoid_VoidP_DataP(lambda ctx, p: print("{epoch: %d, value: %s}" % (p.contents.epoch, parse_value(p))))
			callback = FnVoid_VoidP_DataP(self.parse)

			# Subscribe to logger
			libmetawear.mbl_mw_logger_subscribe(self.logger, None, callback)

			# Download data
			libmetawear.mbl_mw_logging_download(self.device.board, 0, byref(download_handler))
			e.wait()

			return True # Signal sucess

		except RuntimeError as err:
			print(err)
			return False

	# Reset the device
	def reset(self):
		e = Event()
		self.device.on_disconnect = lambda status: e.set()
		libmetawear.mbl_mw_debug_reset(self.device.board)
		e.wait()

		# Set the flag to set the right time when downloading
		self.firstParse = True
		self.f.close()
		return True