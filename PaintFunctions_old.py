import sys
import os
import csv
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import Qt, QPoint, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime

class DrawingArea(QWidget):
	def __init__(self, parent=None):
		super(DrawingArea, self).__init__(parent)
		self.setAttribute(QtCore.Qt.WA_StaticContents)
		self.modified = False
		self.drawing = False
		self.myPenWidth = 4
		self.myPenColor = Qt.blue

		#self.image = image_label

		# Scale factor of the spiral
		self.scale_factor = 0.45

		# Load the background image
		self.background_image = QImage('spiral_temp_ccw.png')
		self.image = QPixmap(self.size())
		self.image.fill(Qt.white)

		self.lastPoint = QPoint()
		self.drawn_points = []  # To store the time and coordinates of drawn points

	def resizeEvent(self, event):
		# Scale the background image to fit the widget size
		scaled_background = self.background_image.scaled(
			int(self.size().width() * self.scale_factor),
			int(self.size().height() * self.scale_factor),
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation
		)
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
		#scaled_background = self.background_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		scaled_background = self.background_image.scaled(
			int(self.size().width() * self.scale_factor),
			int(self.size().height() * self.scale_factor),
			Qt.KeepAspectRatio,
			Qt.SmoothTransformation
		)
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
		#offset_x = (self.width() - self.background_image.width()) // 2
		#offset_y = (self.height() - self.background_image.height()) // 2
		offset_x = 0
		offset_y = 0
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