import cv2
import numpy as np
from matplotlib import pyplot as plt
import serial

ser = serial.Serial(port = None, baudrate = 115200)

sizeAcabado = 0 #ser.read(size = 1)
if(sizeAcabado == "G"):
	Size = 12
	Acabado = True
elif(sizeAcabado == "M"):
	Size = 10
	Acabado = True
elif(sizeAcabado == "P"):
	Size = 8
	Acabado = True
elif(sizeAcabado == "g"):
	Size = 12
	Acabado = False
elif(sizeAcabado == "m"):
	Size = 10
	Acabado = False
elif(sizeAcabado == "p"):
	Size = 8
	Acabado = False
else:
	Size = 0
	Acabado = True

#ser.write("k")


IM_NAME = 'Fotos/peqPin.png'

#Leer la imagen
img = cv2.imread(IM_NAME)

####################################################################################################################################################
#Obtener las dimensiones de la tabla

#Obtener las posiciones de los pixeles, inicial y final, que no sean cero
imHeight, imWidth, imChannels = img.shape

img = img[0:imHeight, 200:imWidth]

cv2.imshow("Display window", img)
cv2.waitKey(0);
cv2.destroyAllWindows()

imHeight, imWidth, imChannels = img.shape
rowFirst = imHeight
colFirst = imWidth
rowLast = 0
colLast = 0

#Leer la imagen como escala de grises
imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#Binarizar la imagen
th,imBinary = cv2.threshold(imgray, 200, 255, 1)			

for i in range(imHeight-1, 0, -1):
	for j in range(0, imWidth):
		I = imBinary[i, j]
		if(I != 0):
			if(rowFirst > i):
				rowFirst = i
			if(colFirst > j):
				colFirst = j

for i in range(0, imHeight):
	for j in range(imWidth-1, 0, -1):
		J = imBinary[i, j]
		if(J != 0):
			if(rowLast < i):
				rowLast = i
			if(colLast < j):
				colLast = j


largo = (rowLast - rowFirst)					#para la grande: 718, 718, 718 la mediana: 718, la chiquita: 625, 609, 607
print "Largo: ",
print largo

ancho = (colLast - colFirst)					#para la grande: 899, 903, 894 la mediana: 752, la chiquita: 775, 747, 744
print "Ancho: ",
print ancho

if(largo < 650):								
	size = 8
elif(ancho > 850):
	size = 12
else:
	size = 10

sizeCon = True

if(size != Size):
	#ser.write("T")
	#ser.read_until(expected = "k", size = 1)
	#sizeCon = False
	print "Error de dimensiones"
							
###################################################################################################################################################
if(sizeCon):
	#Buscar errores

	#Aplicarle un filtro Gaussiano a la imagen
	imBlurred = cv2.GaussianBlur(imBinary, (5, 5), 4)
	imgrayBlurred = cv2.GaussianBlur(imgray, (5, 5), 4)

	edges = cv2.Canny(imgray, 50, 93, apertureSize = 3)


	#Cantidad de Errores
	circles = cv2.HoughCircles(image = imgrayBlurred, method = cv2.HOUGH_GRADIENT, dp = 1, minDist = 50, minRadius = 3, maxRadius = 100, param1 = 100, param2 = 20)
	if circles is not None:
		print "Cantidad de defectos circulares: ",
		c = len(circles)
		print c
	else:
		c = 0
		print "No hay errores circulares"


	edges = cv2.medianBlur(edges, 3)
	edges = cv2.blur(edges, (3, 3))

	cv2.imshow("Display window", edges)
	cv2.waitKey(0);
	cv2.destroyAllWindows()

	x11 = 0
	x22 = 0
	y11 = 0
	y22 = 0
	l = 0

	lines = cv2.HoughLinesP(edges, 1, np.pi/180, 25, maxLineGap = 100)
	if lines is not None:
		lines = sorted(lines, key = lambda lines: lines[:, 2])
		for line in lines:
			x1, y1, x2, y2 = line[0]
			if((abs(x11-x1) > 6 or x11 == 0) and (abs(x22-x2) > 6 or x22 == 0) and (abs(y11-y1) > 6 or y11 == 0) and (abs(y22-y2) > 6 or y22 == 0)):
				x11 = x1
				x22 = x2
				y11 = y1
				y22 = y2
				l = l + 1
				cv2.line(imgray, (x1, y1), (x2, y2), (0, 255, 0), 3)
		print "Cantidad de defectos rectos: ",
		print l
	else:
		print "No hay defectos rectos"

	cantErrores = l + c

	if cantErrores != 0:
		print "Tabla defectuosa"
		#ser.write("D")
		#ser.read_until(expected = "k", size = 1)
		E = True
		print "Cantidad total de errores: ",
		print cantErrores
		#ser.write("C|" + cantErrores)
		#ser.read_until(expected = "k", size = 1)
	else:
		E = False

	#Detectar errores circulares
	if circles is not None:
		circles = np.round(circles[0, :]).astype("int")
		for (x, y, r) in circles:
			cv2.circle(img = imgrayBlurred, center = (x, y), radius = r, color = 0, thickness = 3)
			print "Punto donde se encuentra un defecto circular: ",
			print(x, y)
			#ser.write("Z|" + x)
			#ser.read_until(expected = "k", size = 1)
			#ser.write("W|" + y)
			#ser.read_until(expected = "k", size = 1)
			print "Radio aproximado del defecto: ",
			print r
			#ser.write("X|" + r)
			#ser.read_until(expected = "k", size = 1)
			#ser.write("Y|" + r)
			#ser.read_until(expected = "k", size = 1)

	plt.imshow(imgrayBlurred, cmap = 'gray')
	plt.xticks([]), plt.yticks([])

	cv2.imshow("Display window", imgrayBlurred)
	cv2.waitKey(0);
	cv2.destroyAllWindows()

	#Detectar rectas en la imagen
	lines = cv2.HoughLinesP(edges, 1, np.pi/180, 25, maxLineGap = 100)

	x11 = 0
	x22 = 0
	y11 = 0
	y22 = 0

	if lines is not None:
		lines = sorted(lines, key = lambda lines: lines[:, 2])
		for line in lines:
			x1, y1, x2, y2 = line[0]
			if((abs(x11-x1) > 6 or x11 == 0) and (abs(x22-x2) > 6 or x22 == 0) and (abs(y11-y1) > 6 or y11 == 0) and (abs(y22-y2) > 6 or y22 == 0)):
				x11 = x1
				x22 = x2
				y11 = y1
				y22 = y2
				print "Coordenadas de defecto recto: ",
				print(x1, y1)
				#ser.write("Z|" + x1)
				#ser.read_until(expected = "k", size = 1)
				#ser.write("W|" + y1)
				#ser.read_until(expected = "k", size = 1)
				print "Ancho del defecto: ",
				print abs(x1-x2)
				#ser.write("X|" + abs(x1-x2))
				#ser.read_until(expected = "k", size = 1)
				print "Alto del defecto: ",
				print abs(y1-y2)
				#ser.write("Y|" + abs(y1-y2))
				#ser.read_until(expected = "k", size = 1)
				cv2.line(imgray, (x1, y1), (x2, y2), (0, 255, 0), 3)


	plt.imshow(imgray, cmap = 'gray')
	plt.xticks([]), plt.yticks([])

	cv2.imshow("Display window", imgray)
	cv2.waitKey(0);
	cv2.destroyAllWindows()
	###################################################################################################################################################
	if(not(E)):
		#Verificar el acabado
		#Imagen en tonos de grises, respecto de las intensidades de azul
		justBlue = np.array([1, 0, 0]).reshape((1, 3))
		blue = cv2.transform(img, justBlue)
		blue = cv2.GaussianBlur(blue, (5, 5), 4)

		color = True

		imgBlurred = cv2.GaussianBlur(img, (5, 5), 4)

		if(Acabado):
			#Para color
			for i in range(rowFirst+100, rowLast-100):
				for j in range(colFirst+150, colLast-100):
					red = imgBlurred[i, j, 2]
					green = imgBlurred[i, j, 1]
					bluePixel = imgBlurred[i, j, 0]
					if(not(red < 135 and green < 160 and bluePixel > 20)):
						color = False
						break
				if(color == False):
					break
		else:
			#Para sin color
			for i in range(rowFirst+100, rowLast-100):
				for j in range(colFirst+150, colLast-100):
					red = imgBlurred[i, j, 2]
					green = imgBlurred[i, j, 1]
					bluePixel = imgBlurred[i, j, 0]
					if(red < 175 and green < 155 and bluePixel > 50):
						color = False
						break
				if(color == False):
					break

		#imCropped = blue[rowFirst+20:rowLast-20, colFirst+20:colLast-20]

		if(color):
			cv2.imshow("Display window", blue)
			cv2.waitKey(0);
			cv2.destroyAllWindows()
			print "Color correcto"
			acabado = True
			#Constante que equivale al acabado
			const = 105

			for i in range(colFirst+30, colLast-30):
				for j in range(rowFirst+30, rowLast-30):
					I =  blue[j, i]
					if (I > const):
						print I
						print i 
						print j
						acabado = False
						break
				if (I > const):
					acabado = False
					break

			if(acabado):
				#ser.write("R")
				#ser.read_until(expected = "k", size = 1)
				print "Buen acabado"
			else:
				print "Mal acabado"
				#ser.write("O")
				#ser.read_until(expected = "k", size = 1)
		else:
			print "Color incorrecto"
			#ser.write("c")
			#ser.read_until(expected = "k", size = 1)

###################################################################################################################################################
#S=VI*