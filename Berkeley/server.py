# Implementación del algoritmo de Berkeley - SERVIDOR

import zmq
from zmq.utils.monitor import recv_monitor_message
import random
import time
from datetime import datetime as dt, timedelta as tdel
import string
import threading
import copy
import struct

noClients = 0

# Monitor que cuenta a los clientes
def serverMonitor(monitor):
	global noClients
	EVENT_MAP = {}
	#print("Event names:")
	for name in dir(zmq):
	    if name.startswith('EVENT_'):
	        value = getattr(zmq, name)
	        #print("%21s : %4i" % (name, value))
	        EVENT_MAP[value] = name

	while monitor.poll():
		event = recv_monitor_message(monitor)
		event.update({'description': EVENT_MAP[event['event']]})
		#print("Event: {}".format(event))
		if event['event'] == zmq.EVENT_MONITOR_STOPPED:
			break
		if event['event'] == zmq.EVENT_ACCEPTED:
			noClients  += 1
			#print("Cliente conectado.\n")
			#print("No. de clientes: ", noClients)
		elif event['event'] == zmq.EVENT_DISCONNECTED:
			noClients -=1
			#print("Cliente desconectado.\n")
			#print("No. de clientes: ", noClients)

def receiveClientTimes(timeDiffsList, currClients, clientDic):
	x = 0
	while x < currClients:
		if noClients == 0:
			break
		print("Esperando respuesta...")
		#timeDiff_str = server.recv_string() # para REP
		timeDiff_lst = server.recv_multipart()
		#print("Respuesta recibida: ", timeDiff_lst)
		#timeDiff = float(timeDiff_str)
		timeDiff = float(timeDiff_lst[1].decode())
		# Guarda la identidad del cliente como clave y la diferencia (D1, D2, D3...) como valor
		clientDic[timeDiff_lst[0]] = timeDiff
		#print("Diccionario de clientes y su diferencia de tiempo: ", clientDic)
		timeDiffsList.append(timeDiff)
		x += 1

def getAverage(timeDiffsList, trip_time, currClients):
	x = 1
	average = 0
	while x < len(timeDiffsList):
		timeDiffsList[x] -= trip_time
		average += timeDiffsList[x]
		print("D", x, "\' = ", timeDiffsList[x], sep = '')
		x += 1

	#for x in timeDiffsList[1:]:
	#	average += x - trip_time
	#	print(x, average)

	average = average / (currClients + 1)
	return average

def sendAverage(timeDiffsList, averageDiff, clientDic):
	x = len(timeDiffsList) - 1
	#while x < len(timeDiffsList):
	#	timeDiffsList[x] = averageDiff - timeDiffsList[x]
	#	x += 1
	#print("Ajustes: ", timeDiffsList)
	#for diff in timeDiffsList[1:]:
	#	individualAvrg = diff
	#	print("Ajuste enviado: ", individualAvrg)
	#	server.send_string(str(individualAvrg))
	while len(clientDic) > 0:
		client_diff = clientDic.popitem()
		individualAvrg = averageDiff - timeDiffsList[x]
		x -= 1
		#print("Cliente:", client_diff[0], "\tAjuste:", individualAvrg)
		print("\tAjuste:", individualAvrg)
		server.send_multipart([client_diff[0], struct.pack('f', individualAvrg)])

# Función main
if __name__ == '__main__':

	context = zmq.Context()

	# Construcción del socket servidor
	server = context.socket(zmq.ROUTER)
	server.bind("tcp://*:5557")

	# Construcción del socket publisher
	serverPub = context.socket(zmq.PUB)
	serverPub.bind("tcp://*:5558")

	# Construcción del socket contador
	monitor = serverPub.get_monitor_socket()

	print("\nSERVIDOR EN LÍNEA.\n")

	clientDic = { 'Init' : 'Init' }

	monitor_thread = threading.Thread( target = serverMonitor, args = (monitor,), daemon = True )
	monitor_thread.start()

	while True:

		# Inicio de nuevo ciclo
		print("\n***Iniciando ciclo de sincronización...***")

		if noClients == 0:
			print("No hay clientes, esperando clientes...")
			time.sleep(2)
			continue

		clientDic.clear()

		# Obtiene T0 y lo manda como cadena a los clientes mediante el socket PUB
		server_clock_t0 = dt.now()
		print("Reloj del servidor en T0: ", server_clock_t0)
		server_clock_t0_string = server_clock_t0.strftime("%m/%d/%y %H:%M:%S:%f")
		# Obtiene el número de clientes a los que lo va a mandar y lo manda
		currClients = copy.deepcopy(noClients)
		print("Número de clientes conectados: ", currClients, "\n")
		serverPub.send_string(server_clock_t0_string)

		# Se obtiene un número aleatorio para simular el tiempo de envío del servidor al cliente
		time_server_client = random.randint(0, 10) * 0.1
		print("Tiempo de envío del servidor al cliente: ", time_server_client)

		# Inicializa lista de diferencias incluyendo al reloj del servidor
		timeDiffsList = [0]

		# Obtiene las diferencias de los clientes
		receiveClientTimes(timeDiffsList, currClients, clientDic)
		print("Diferencias de tiempo: ", timeDiffsList)

		# Se obtiene un número aleatorio para simular el tiempo de envío del cliente al servidor
		time_client_server = random.randint(0, 10) * 0.1
		print("Tiempo de envío del cliente al servidor: ", time_client_server)

		# Se obtiene el tiempo T1i, que corresponde al tiempo en que el servidor recibe las respuestas de los clientes
		time_delta_T1i = tdel(seconds = (time_server_client + time_client_server))
		server_clock_t1i = server_clock_t0 + time_delta_T1i
		print("Reloj del servidor en T1i: ", server_clock_t1i)

		# Calcula el tiempo entre los envíos y las respuestas
		trip_time_td = (server_clock_t1i - server_clock_t0) / 2
		trip_time = trip_time_td.total_seconds()
		print("Tiempo de viaje (T1i - T0)/2 (Round Trip Time): ", trip_time)

		# Obtiene el promedio
		averageDiff = getAverage(timeDiffsList, trip_time, currClients)
		print("Promedio: ", averageDiff)
		
		# Ajusta el reloj del servidor		
		server_clock_final = dt.now()
		time_delta_f = tdel(seconds = averageDiff)
		print("La hora antes del ajuste es:", (server_clock_final))
		print("La hora ajustada es:", (server_clock_final + time_delta_f))

		# Envía el promedio de cada cliente
		sendAverage(timeDiffsList, averageDiff, clientDic)

		print("La hora tras el RTT del envío a los clientes, aún ajustada:", (server_clock_final + time_delta_f + tdel(seconds = trip_time)))

		time.sleep(5)
