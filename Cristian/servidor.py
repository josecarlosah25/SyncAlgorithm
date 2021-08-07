import zmq
import random
import time
import string

context= zmq.Context()

#Construimos el Socket 
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

print("Listo para ser preguntado por la hora")
i=0
while True:
	#calculamos el tiempo que tarda en llegar (fingido para pura demostración)
	sleeptime = random.randint(5,10)/2

	#Recibimos la petición 
	_=socket.recv()

	#Dormimos el proceso un poco
	time.sleep(sleeptime)
	#Obtenemos la hora del servidor
	t = time.time()
	print("Enviando Hora:"+str(time.ctime(t)))
	#Dormimos la misma cantidad de tiempo que cuando nos llego la peticion para hacerlo simetrico (teoricamente seria la forma ideal)
	time.sleep(sleeptime)
	#enviamos el reloj
	socket.send_string(str(t))
