# Python3 program imitating a clock server
 
import socket
import datetime
import ntplib
import time
   
# função para iniciar o servidor de relógio
def initiateClockServer():
 
    s = socket.socket()
    print("Socket successfully created")
       
    # Definir a porta do servidor
    port = 8000
 
    s.bind(('', port))
      
    # Definir o número máximo de conexões
    s.listen(5)     
    print("Socket is listening...")

    # Loop infinito para aceitar conexões
    while True:
        #pegue o horario atual do ntp
        ntp_server = 'pool.ntp.org'
        ntp_client = ntplib.NTPClient()

        # Obtém o tempo atual a partir do servidor NTP
        response = ntp_client.request(ntp_server)

        # Obtém o timestamp da resposta e converte para a hora local
        ntp_time = time.localtime(response.tx_time)

        time_string = time.strftime('%Y-%m-%d %H:%M:%S', ntp_time)
         
       # Aceitar conexões do cliente
        connection, address = s.accept()     
        print('Server connected to', address)
       
       # Enviar a hora atual para o cliente
        connection.send(str(time_string).encode())
       
       # Fechar a conexão
        connection.close()
 
 
if __name__ == '__main__':
    initiateClockServer()