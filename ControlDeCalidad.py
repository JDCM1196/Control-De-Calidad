import cv2
import numpy as np
from matplotlib import pyplot as plt

IM_NAME = 'image5.png'

#Leer la imagen
img = cv2.imread(IM_NAME)
cv2.imshow("Display window", img)
cv2.waitKey(0);
cv2.destroyAllWindows()


####################################################################################################################################################
#Obtener las dimensiones de la tabla

#Leer la imagen como escala de grises
imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#Definir la escala para pixeles:cm
escala = 1

#Binarizar la imagen
th,imBinary = cv2.threshold(imgray, 40, 255, 1)								#El threshold hay que alterarlo al hacer pruebas con la tabla pintada


#Obtener las posiciones de los pixeles, inicial y final, que no sean cero
nonZPos = np.transpose(np.nonzero(imBinary))
rowFirst = nonZPos[0, 0]
colFirst = nonZPos[0, 1]

nonZMax = np.amax(nonZPos, axis = 0)
rowLast = nonZMax.item(0)
colLast = nonZMax.item(1)

print rowFirst
print colFirst
print rowLast
print colLast

largo = (rowLast - rowFirst)*escala
ancho = (colLast - colFirst)*escala

###################################################################################################################################################
#Verificar el acabado

#Imagen en tonos de grises, respecto de las intensidades de azul
justBlue = np.array([1, 0, 0]).reshape((1, 3))
blue = cv2.transform(img, justBlue)

#Cortar la imagen acorde a las dimensiones de la tabla
####################imCropped = blue[rowFirst:rowLast, colFirst:colLast]

#Mientras no se tenga foto sin orilla negra de una tabla azul:
imCropped = blue[rowFirst:rowLast, colFirst:colLast]

#cv2.imshow("Display window", imCropped)
#cv2.waitKey(0);
#cv2.destroyAllWindows()

#Constante que equivale al color de la pintura
const = 210

acabado = True

####################for i in range(colFirst, colLast):
####################for j in range(rowFirst, rowLast):
for i in range(colFirst, colLast):
	for j in range(rowFirst, rowLast):
		I =  blue[j, i]
		if (I > const):
			acabado = False
			break
	if (I > const):
		acabado = False
		break

if(acabado == True):
	print("Buen acabado")
else:
	print("Mal acabado")

###################################################################################################################################################
#Buscar errores

#Aplicarle un filtro Gaussiano a la imagen
imBlurred = cv2.GaussianBlur(imBinary, (5, 5), 4)
imgrayBlurred = cv2.GaussianBlur(imgray, (5, 5), 4)


edges = cv2.Canny(imgray, 150, 200, apertureSize = 3)

#Detectar errores circulares
circles = cv2.HoughCircles(image = imgrayBlurred, method = cv2.HOUGH_GRADIENT, dp = 1, minDist = 200, minRadius = 5, maxRadius = 50, param1 = 100, param2 = 23)

print circles
if circles is not None:
	circles = np.round(circles[0, :]).astype("int")
	for (x, y, r) in circles:
		cv2.circle(img = imgrayBlurred, center = (x, y), radius = r, color = 0, thickness = 3)	#era imBlurred
		print("Punto donde se encuentra un defecto circular: ")
		print(x, y)
plt.imshow(imgrayBlurred, cmap = 'gray')
plt.xticks([]), plt.yticks([])
plt.show()


#Detectar rectas en la imagen
edges2 = cv2.Canny(imgrayBlurred, 300, 200)

lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, maxLineGap = 250)
lines2 = cv2.HoughLinesP(edges2, 1, np.pi/180, 20, maxLineGap = 250)

for line in lines:
	if(line not in lines2):
		x1, y1, x2, y2 = line[0]
		cv2.line(imgray, (x1, y1), (x2, y2), (0, 255, 0), 3)

plt.imshow(imgray, cmap = 'gray')
plt.xticks([]), plt.yticks([])
plt.show()

#S=VI*