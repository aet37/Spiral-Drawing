from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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