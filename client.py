# Implementación del algoritmo de Berkeley - CLIENTE

import zmq
import random
import time
from datetime import datetime as dt, timedelta as tdel
import string
import threading
import struct

# Función main
if __name__ == '__main__':

	context = zmq.Context()

	# Construcción del socket cliente
	client = context.socket(zmq.DEALER)
	client.connect("tcp://localhost:5557")

	# Construcción del socket subscriber
	clientSub = context.socket(zmq.SUB)
	clientSub.connect("tcp://localhost:5558")
	clientSub.subscribe("")

	print("\nConectando...\n")

	while True:

		# Inicio de nuevo ciclo, espera hasta obtener mensaje del socket PUB del servidor
		server_clock_t0_string = clientSub.recv_string()
		print("\n***Iniciando ciclo de sincronización...***")
		print("Reloj recibida del servidor en T0: ", server_clock_t0_string)
		#server_clock_t0 = dt.strptime(server_clock_t0_string, '%m/%d/%y %H:%M:%S:%f')

		# Obtiene la diferencia, se obtiene de forma aleatoria por motivos didácticos
		client_t0_diff = random.randint(-10, 10) * 0.1
		client_t0_diff_string = str(client_t0_diff)
		print("Diferencia del cliente con el servidor: ", client_t0_diff)

		# Manda la diferencia de regreso
		client.send_string(client_t0_diff_string)

		# Recibe el ajuste
		print("Esperando respuesta...")
		time_adjustment_lst = client.recv_multipart()
		print("Respuesta recibida: ", time_adjustment_lst)
		time_adjustment = struct.unpack('f', time_adjustment_lst[0])
		time_adjustment = time_adjustment[0]
		print("Ajuste recibido: ", time_adjustment)

		# Ajusta el reloj del cliente
		client_clock_final = dt.now()
		time_delta_f = tdel(seconds = time_adjustment + client_t0_diff)
		print("La hora ajustada es: ", (client_clock_final + time_delta_f))