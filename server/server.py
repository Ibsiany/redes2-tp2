import math
import socket
import os

PASSWORD = '1234' # Senha de acesso ao servidor
HOST = ''  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
orig = (HOST, PORT)
udp.bind(orig)
diretorio = './files'

dest = ('localhost', 6000)

print('Socket UDP na porta 5000')

def listFiles(): # Função para listar arquivos disponíveis
    arquivos = os.listdir(diretorio)
    array = [];
    for arquivo in arquivos:
        if os.path.isfile(os.path.join(diretorio, arquivo)):
            array.append(arquivo)
    
    return array;

files = listFiles();


def check_password(sentence): # Função de verificação de senha
    if(sentence == PASSWORD):
        udp.sendto(bytes('SENHA OK', 'ascii'), dest)
        list = ', '.join(listFiles())
        udp.sendto(bytes(list, 'ascii'), dest)
    else:
        udp.sendto(bytes('SENHA INCORRETA', 'ascii'), dest)

def select_file(filename):  # Função para selectionar arquivo
    if filename not in files:
        udp.sendto(bytes('Arquivo nao encontrado.', 'ascii'), dest)
        return False

    udp.sendto(bytes('Arquivo sera enviado.', 'ascii'), dest)
    send_file(filename);

def send_file(filename): # Função para enviar o arquivo selecionado
    print(filename)    
    return True;

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
            case 'select_file':
                select_file(message)
    except Exception as e:
        udp.sendto(bytes('Servidor com erro.', 'ascii'), dest)
        
        print('erro: ' + str(e))
        
        continue

    

