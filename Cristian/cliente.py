import time
import zmq
import random

context = zmq.Context()

#Construimos el Socket
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5558")


i = 0
while True:

	# Inicio de nuevo ciclo
	print("\n***Pidiendo hora...***")

	#Tomamos el tiempo mr
	mr = time.time()

	#Modificamos este valor de forma "demostrativa" y comprobar el funcionamiento del algoritmo (para que no sea el mismo tiempo que el servidor)
	prueba = random.randint(-5,12)
	mr = mr + prueba	

	#Enviamos el mensaje al servidor
	socket.send_string(str(mr))
	#print("Hora actual = "+str(time.ctime(mr)))

	#Recibimos el tiempo y calculamos el Tround que es el tiempo que tarda el mensaje en regresar
	mt = float(socket.recv())
	trecibido = time.time() + prueba
	Tround = trecibido - mr

	print("Tiempo de envío: "+str(time.ctime(mr)))
	print("Tiempo de recepción: "+str(time.ctime(trecibido)))
	print("Tround: "+str(Tround)+" [segundos]")
	print()

	#Calculamos la nueva hora con respecto al recibido y el Tround
	t = mt + (Tround/2)
	print("La hora recibida mt es: "+str(time.ctime(mt)))
	print("La hora actualizada es: "+str(time.ctime(t)))

	time.sleep(5)
