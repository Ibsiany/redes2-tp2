import socket
import base64
import random
import time
import sys
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import filesFuncs
HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
LOSS = 0.05  # Probabilidade de perda de pacotes
RTT = 0.1  # Tempo de ida e volta
diretorio = './files'

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
diretorio = './files'

# Definindo uma porta para ser ouvida
udp.bind(('', 6000))

print('Socket UDP na porta 6000')

def select_file(filename):  # Função para selectionar arquivo
    if filename not in files:
        udp.sendto(bytes('FIM|FIM|FIM', 'ascii'), dest)
        
        raise Exception('Arquivo nao encontrado.')

    udp.sendto(bytes('ARQUIVO ENCONTRADO: ' + filename, 'ascii'), dest)
    send_file(filename)

files = filesFuncs.listFiles()

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

def receber_arquivo(filename):
    buffer = []
    base64_decode = ''
    expected_seq_num = 0
    
    while base64_decode != 'FIM|FIM':
        try:
            base64_string, cliente = udp.recvfrom(5 * 1024)
            udp.settimeout(10*RTT)
        except Exception as e:
            print('TIMEOUT, SOLICITANDO PACOTE AO SERVIDOR NOVAMENTE...')
            udp.sendto(bytes(str(expected_seq_num) + '|NACK', 'ascii'), dest)
            continue

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

opcao = '1'
while(opcao != '3'):   
    opcao = input('\nSelecione a opcao desejada:\n1.Enviar Arquivo.\n2.Receber Arquivo.\n3.Sair\n')

    match opcao:
            case "1":
                password = input('Digite a senha: ')
                udp.sendto(bytes('password|' + password, 'ascii'), dest)

                msg_confirmation, cliente = udp.recvfrom(5 * 1024 * 1024)
                print(cliente, msg_confirmation.decode('ascii'))

                if(msg_confirmation.decode('ascii') == 'SENHA INCORRETA'):
                    print('Conexao finalizada, senha incorreta!')
                    udp.close()
                else:
                    list = ', '.join(filesFuncs.listFiles())
                    print(list)
                    
                    filename = input('Qual arquivo deseja enviar: ')
                    if filename not in files:
                        print('Arquivo nao encontrado.')
                        
                        raise Exception('Arquivo nao encontrado.')

                    udp.sendto(bytes('received_file|'+filename, 'ascii'), dest)
                    select_file(filename)
            case "2":
                try:
                    udp.sendto(bytes('list_file|', 'ascii'), dest)
                    list_files_received, cliente = udp.recvfrom(5 * 1024 * 1024)
                    print(cliente, list_files_received.decode('ascii'))
 
                    arquivo = input('Digite o arquivo desejado: ')
                    udp.sendto(bytes('select_file|'+arquivo, 'ascii'), dest)

                    msg_arquivo, cliente = udp.recvfrom(5 * 1024 * 1024)
                    print(cliente, msg_arquivo.decode('ascii'))
                    
                    receber_arquivo(arquivo)
                except Exception as e:
                    print('Erro interno: ' + str(e))
            case "3":
                udp.close()
                exit()
            case _:
                print('Opcao invalida!')