from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import butter, lfilter, freqz, welch
import csv

class MplCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		self.fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = self.fig.add_subplot(111)
		super(MplCanvas, self).__init__(self.fig)

	def clear_plot(self):
		self.fig.clf()
		self.axes = self.fig.add_subplot(111)
		self.draw()

# Function to read data from a file
def load_data_spiral(fpath):
	x = []
	y = []

	# Get the points in the current spiral
	with open(fpath, newline='') as csvfile:
		spiral_reader = csv.reader(csvfile, delimiter=',')
		for row in spiral_reader:
			if row[1] != 'X':
				x.append(int(row[1]))
				y.append(int(row[2]))

	return x, y

# Function to read data from a file
def load_data_accel(fpath):
	t = []
	x = []
	y = []
	z = []
	# Get the points in the current spiral
	with open(fpath, newline='') as csvfile:
		spiral_reader = csv.reader(csvfile, delimiter=',')
		for row in spiral_reader:
			t.append(float(row[0]))
			x.append(float(row[1]))
			y.append(float(row[2]))
			z.append(float(row[3]))

	return t, x, y, z

# Function to read data from a file
def load_data_accel_psd(fpath):
	f = []
	psd = []

	# Get the points in the current spiral
	with open(fpath, newline='') as csvfile:
		spiral_reader = csv.reader(csvfile, delimiter=',')
		for row in spiral_reader:
			f.append(float(row[0]))
			psd.append(float(row[1]))

	return f, psd

# Function to analyze functions
def analyze_accel_data(t, x, y, z):

	# Turn into numpy arrays
	t = np.array(t_pa)
	x = np.array(x_pa)
	y = np.array(y_pa)
	z = np.array(z_pa)
	accel_data = x + y + z

	# Set parameters
	fs = 100
	low_f = 3
	high_f = 14
	order = 4

	# Filter the data
	b, a = butter(order, [low_f, high_f], fs=fs, btype='band')
	accel_data_filt = lfilter(b, a, accel_data)

	# Take the regio of interest
	f_filt_ret = f_filt[idx]
	welch_accel_ret = welch_accel_filt_sm[idx]

	# Get statstics of accel trace
	peak_val = round(max(welch_accel_ret), 3)
	auc_welch = round(np.trapz(welch_accel_ret), 3)
	auc_accel = round(np.trapz(abs(accel_data_filt)) / len(accel_data_filt), 3)

	return f_filt_ret, welch_accel_ret, peak_val, auc_welch, auc_accel









