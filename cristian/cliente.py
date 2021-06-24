
import time
import zmq

context = zmq.Context()

#Construimos el Socket
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5558")


i=0
while True:

	print ("Presione Enter para pedir la hora ")
	_ = input()

	#Tomamos el tiempo mr
	mr=time.time()

	#Modificamos este valor de forma "demostrativa" y comprobar el funcionamiento del algoritmo"
	prueba=10+(mr*.01)
	mr=mr+prueba
	

	#Enviamos el mensaje al servidor
	socket.send_string(str(mr))
	print("Hora actual = "+str(time.ctime(mr)))

	#Recibimos el tiempo y calculamos el Tround que es el tiempo que tarda el mensaje en regresar
	mt= float(socket.recv())
	Tround= (time.time()+prueba)-mr

	print("Tround: "+str(Tround)+" [segundos]")

	#Calculamos la nueva hora con respecto al recibido y el Tround
	t=mt+ (Tround/2)
	print("La hora recibida mt es: "+str(time.ctime(mt)))
	print("La hora actualizada es: "+str(time.ctime(t)))

	#Sentencias para controlar cuantas veces hacemos lo mismo antes de dejar morir el proceso
	i=i+1
	if i>0:
		break








