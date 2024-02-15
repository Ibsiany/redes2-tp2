import socket
import base64
import random
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import filesFuncs

PASSWORD = '1234' # Senha de acesso ao servidor
HOST = ''  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
LOSS = 0.05  # Probabilidade de perda de pacotes
RTT = 0.1  # Tempo de ida e volta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
orig = (HOST, PORT)
udp.bind(orig)
diretorio = './files'

dest = ('localhost', 6000)

print('Socket UDP na porta 5000')

files = filesFuncs.listFiles();

def select_file(filename):  # Função para selectionar arquivo
    if filename not in files:
        udp.sendto(bytes('FIM|FIM|FIM', 'ascii'), dest)
        
        raise Exception('Arquivo nao encontrado.')

    udp.sendto(bytes('ARQUIVO ENCONTRADO: ' + filename, 'ascii'), dest)
    send_file(filename)


def send_file(filename): # Função para enviar o arquivo selecionado
    try:
        with open(diretorio+"/"+filename, "rb") as arquivo:
            conteudo_arquivo = arquivo.read()
            arquivo_codificado = base64.b64encode(conteudo_arquivo)
            
            file = arquivo_codificado.decode("utf-8")
            
            arquivo_segmentado = filesFuncs.segmentar_arquivo(file)
            print('Arquivo segmentado' + str(len(arquivo_segmentado)))
            
            seq_num = 0

            start_time = time.time()
            for i in range(0, len(arquivo_segmentado)):
                time.sleep(RTT)
                checksum = filesFuncs.calculate_checksum(arquivo_segmentado[i].encode('ascii'))

                if(random.random() < LOSS):
                    udp.sendto(bytes(str(seq_num) + "|" + str(checksum) + "|" + 'currpted_data', 'ascii'), dest)
                elif(random.random() < LOSS):
                    print('Pacote perdido...' + str(seq_num))
                else:
                    udp.sendto(bytes(str(seq_num) + "|" + str(checksum) + "|" + arquivo_segmentado[i], 'ascii'), dest)
                
                ack, cliente = udp.recvfrom(1024)

                seq, ack = ack.decode('ascii').split('|')

                while ack == 'NACK':
                    print('reenviando pacote...' + str(seq))
                    udp.sendto(bytes(str(seq) + "|" + str(checksum) + "|" + arquivo_segmentado[int(seq)], 'ascii'), dest)
                    ack, cliente = udp.recvfrom(1024)
                
                seq_num += 1
            end_time = time.time()
            print('ARQUIVO ENVIADO.')
            
            total_bytes_sent = os.path.getsize(diretorio+"/"+filename)
            time_elapsed = end_time - start_time
            throughput = total_bytes_sent / time_elapsed

            print(f'Throughput: {throughput} bytes/segundos')

            udp.sendto(bytes('FIM|FIM|FIM', 'ascii'), dest)
                
    except Exception  as e:
        print(str(e))
        raise Exception("Falha ao enviar arquivo {filename}.")

def check_password(sentence): # Função de verificação de senha
    if(sentence == PASSWORD):
        udp.sendto(bytes('SENHA OK', 'ascii'), dest)
    else:
        udp.sendto(bytes('SENHA INCORRETA', 'ascii'), dest)

def receber_arquivo(filename):
    buffer = []
    base64_decode = ''
    expected_seq_num = 0
    
    while base64_decode != 'FIM|FIM':
        base64_string, cliente = udp.recvfrom(5 * 1024)
        seq_num, base64_decode = base64_string.decode('ascii').split('|', 1)
        
        if(base64_decode != 'FIM|FIM'):
            check_sum, base64_decode = base64_decode.split('|')
            if(check_sum != str(filesFuncs.calculate_checksum(base64_decode.encode('ascii'))) or int(seq_num) != expected_seq_num):
                print('PACOTE CORROMPIDO OU FORA DE ORDEM')
                udp.sendto(bytes(str(expected_seq_num) + '|NACK', 'ascii'), dest)  # Send NACK
                continue
            else:
                if int(seq_num) >= len(buffer):
                    buffer.extend([None] * (int(seq_num) - len(buffer) + 1))
                buffer[int(seq_num)] = base64_decode
                print('PACOTE RECEBIDO')
                udp.sendto(bytes(str(expected_seq_num) + '|ACK', 'ascii'), dest)  # Send ACK
                expected_seq_num += 1
        else:
            print('FIM')
            
    try:
        caminho_completo = os.path.normpath(os.path.join(diretorio, filename))
        
        with open(caminho_completo, "wb") as arquivo:
            bufferIsString = ''.join(buffer)
            
            arquivo_decodificado = base64.b64decode(bufferIsString)
            arquivo.write(arquivo_decodificado)

        print ("Arquivo salvo em: " + caminho_completo)
    except Exception as e:
        raise Exception("Erro ao salvar o arquivo:"+str(e))
    
def list_files():
    list = ', '.join(filesFuncs.listFiles())
    udp.sendto(bytes(list, 'ascii'), dest)

while True:
    try:
        message, cliente = udp.recvfrom(1024)
        sentence = message.decode('ascii')
        print(cliente, sentence)    

        idetify = sentence.split("|")[0]
        message = sentence.split('|')[1]
        

        match idetify:
            case "password":
                check_password(message)
            case 'list_file':
                list_files()
            case 'select_file':
                select_file(message)
            case "received_file":
                receber_arquivo(message)
    except Exception as e:
        udp.sendto(bytes('Servidor com erro.', 'ascii'), dest)
        
        print('erro: ' + str(e))
        
        if(str(e) != '[WinError 10040] Uma mensagem enviada em um soquete de datagrama era maior do que o buffer de mensagens internas ou excedia algum outro limite da rede, ou o buffer usado para receber um datagrama era menor do que o próprio datagrama'):
            raise Exception(str(e))
        
    

