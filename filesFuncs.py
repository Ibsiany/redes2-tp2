import os
HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
LOSS = 0.05  # Probabilidade de perda de pacotes
RTT = 0.1  # Tempo de ida e volta
package_size = (1460) - 1
timeout_ms = 2000

diretorio = './files'

def listFiles(): # Função para listar arquivos disponíveis
    arquivos = os.listdir(diretorio)
    array = [];
    for arquivo in arquivos:
        if os.path.isfile(os.path.join(diretorio, arquivo)):
            array.append(arquivo)
    
    return array;

def segmentar_arquivo(file): # Função para segmentar o arquivo
    tam = len(file)
    initial = 0         
    final = package_size

    arquivo_segmentado = []
    while tam > 0:
        if(tam >= package_size):
            arquivo_segmentado.append(file[initial:initial+package_size])
            tam = tam - package_size
            initial = final
            final = final + package_size
        else: 
            arquivo_segmentado.append(file[initial:initial+tam])
            tam = tam - tam
            initial = final
            final = final + tam
        
    return arquivo_segmentado

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
    checksum = (checksum & 0xFF) + (checksum >> 8)
    return (~checksum) & 0xFF
