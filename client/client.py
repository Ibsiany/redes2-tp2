import socket
import datetime
import time
import os
from dateutil import parser
from timeit import default_timer as timer
import win32api

# função para sincronizar o tempo do cliente com o servidor
def synchronizeTime():

    i = 0

    while True:     
        i+=1
        print("\nRequisicao: " + str(i))
        s = socket.socket()
	
	    # porta do servidor
        port = 8000	
	
	    # conectar ao servidor
        s.connect(('192.168.0.105', port))
        request_time = timer()
	
	    # receber a hora do servidor
        server_time = parser.parse(s.recv(1024).decode())
        response_time = timer()
        actual_time = datetime.datetime.now()
        print("Hora do servidor: " + str(server_time))
        process_delay_latency = response_time - request_time
        print("Tempo de resposta: " + str(process_delay_latency) + " segundos")
        print("Hora atual do cliente: " + str(actual_time))
	
	    # sincronizar o tempo do cliente com o servidor
        client_time = server_time + datetime.timedelta(seconds = (process_delay_latency) / 2)
        print("Horário do cliente de processo sincronizado: " + str(client_time))
	
        # calcular o erro de sincronização
        error = actual_time - client_time
        print("Erro de sincronização : "+ str(error.total_seconds()) + " seconds")

        s.close()	

        # verifica o S.O do cliente
        if os.name == 'nt':
            error_seconds = (datetime.datetime.now() - client_time).total_seconds()
            if abs(error_seconds/1800) < 1:
                client_time = datetime.timedelta(hours=3) + client_time
                win32api.SetSystemTime(int(client_time.year), int(client_time.month), 0, int(client_time.day), int(client_time.hour), int(client_time.minute), int(client_time.second), 0)
            else:
                while abs(error_seconds) > 1:
                    if abs(error_seconds/1800) < 1:
                        client_time = datetime.timedelta(hours=3) + client_time
                        win32api.SetSystemTime(int(client_time.year), int(client_time.month), 0, int(client_time.day), int(client_time.hour), int(client_time.minute), int(client_time.second), 0)
                        break
                    if error_seconds > 1:
                        new_time = datetime.datetime.now() + datetime.timedelta(hours=2, minutes=30)
                        print('Atrasando relógio: ')
                        win32api.SetSystemTime(int(new_time.year), int(new_time.month), 0, int(new_time.day), int(new_time.hour), int(new_time.minute), int(new_time.second), 0)
                    else:
                        new_time = datetime.datetime.now() + datetime.timedelta(minutes=30) + datetime.timedelta(hours=3)
                        print('Adiantando relógio: ')
                        win32api.SetSystemTime(int(new_time.year), int(new_time.month), 0, int(new_time.day), int(new_time.hour), int(new_time.minute), int(new_time.second), 0)
                    print("Atualização gradual do cliente. Erro: {} segundos".format(error_seconds))
                    time.sleep(5)
                    error_seconds = (datetime.datetime.now() - client_time).total_seconds()
        else:
            error_seconds = (datetime.datetime.now() - client_time).total_seconds()
            if abs(error_seconds/1800) < 1:
                os.system('sudo date -s "{}"'.format(client_time))
            else:
                while abs(error_seconds) > 1:
                    if abs(error_seconds/1800) < 1:
                        os.system('sudo date -s "{}"'.format(client_time))
                        break
                    if error_seconds > 1:
                        os.system('sudo date -s "{}"'.format(datetime.datetime.now() - datetime.timedelta(seconds=1800)))
                    else:
                        os.system('sudo date -s "{}"'.format(datetime.datetime.now() + datetime.timedelta(seconds=1800)))
                    print("Atualização gradual do cliente. Erro: {} segundos".format(error_seconds))
                    time.sleep(5)

                    error_seconds = (datetime.datetime.now() - client_time).total_seconds()
        time.sleep(10)
	

if __name__ == '__main__':
	synchronizeTime()