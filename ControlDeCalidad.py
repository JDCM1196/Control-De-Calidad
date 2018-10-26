import cv2
import numpy as np
from matplotlib import pyplot as plt

IM_NAME = 'image5.png'

#Leer la imagen
img = cv2.imread(IM_NAME)
cv2.imshow( "Display window", img)

cv2.waitKey(0);


####################################################################################################################################################
#Obtener las dimensiones de la tabla

#Leer la imagen como escala de grises
imgray = cv2.imread(IM_NAME, 0)

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

#print rowFirst
#print colFirst
#print rowLast
#print colLast

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


edges = cv2.Canny(imBlurred, 0, 50)
line_image = np.copy(edges) * 0

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
lines = cv2.HoughLinesP(image = edges, lines = np.array([]), rho = 1, theta = np.pi/180, threshold = 30, minLineLength = 10, maxLineGap = 50)

#for rho, theta in lines[0]:
#    a = np.cos(theta)
#    b = np.sin(theta)
#    x0 = a*rho
#   y0 = b*rho
#    x1 = int(x0 + 2000*(-b))
#    y1 = int(y0 + 2000*(a))
#    x2 = int(x0 - 2000*(-b))
#    y2 = int(y0 - 2000*(a))

    #cv2.line(imBlurred,(x1,y1),(x2,y2),(0, 0, 255), 2)
#    cv2.line(imBlurred,(x1,y1),(x2,y2),(255, 0, 0), 2)
#    print("Coordenada X de donde inicia el error: ")
#    print x0
#    print("Coordenada Y de donde inicia el error: ")
#    print y0

#plt.imshow(back, cmap = 'gray')

for line in lines:
	for x1, y1, x2, y2 in line:
		cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
		print("Coordenadas de donde se encuentra el error: ")
		print(x2-x1, abs(y2-y1))

lines_edges = cv2.addWeighted(edges, 0.8, line_image, 1, 0)

plt.imshow(line_image, cmap = 'gray')
plt.xticks([]), plt.yticks([])
plt.show()

##No funcionan los errores circulares, ni las rectas de la imagen img2.png