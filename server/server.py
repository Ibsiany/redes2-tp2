import socket
import os
import base64
import math

PASSWORD = '1234' # Senha de acesso ao servidor
HOST = ''  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
orig = (HOST, PORT)
udp.bind(orig)
diretorio = './files'

timeout_ms = 2000

file_name = ''

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
    global file_name
    
    file_name = filename
    if filename not in files:
        udp.sendto(bytes('Arquivo nao encontrado.', 'ascii'), dest)
        
        raise Exception('Arquivo nao encontrado.')

    udp.sendto(bytes('ARQUIVO ENCONTRADO: ' + filename, 'ascii'), dest)
    
def segmentar_arquivo(file, partition_number): # Função para segmentar o arquivo
    package_size = (1460) - 1
    tam = len(file)
    array_size = math.ceil(tam / partition_number)
    initial = 0
    
    if(array_size <= package_size):
        package_size = array_size
    else:
         print('\nNúmero de partições informado incompátivel, será realizado o particionamento padrão. \n')
         
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

def send_file(filename,partition_number): # Função para enviar o arquivo selecionado
    try:
        with open(diretorio+"/"+filename, "rb") as arquivo:
            conteudo_arquivo = arquivo.read()
            arquivo_codificado = base64.b64encode(conteudo_arquivo)
            
            file = arquivo_codificado.decode("utf-8")
            
            arquivo_segmentado = segmentar_arquivo(file,partition_number)
            print('Arquivo segmentado' + str(len(arquivo_segmentado)))
            
            for segmento in arquivo_segmentado:
                checksum = calculate_checksum(segmento.encode('ascii'))
                udp.sendto(bytes(str(checksum) + "|" + segmento, 'ascii'), dest)      
            
            print('ARQUIVO ENVIADO.')
            udp.sendto(bytes('FIM', 'ascii'), dest)
                
    except Exception  as e:
        print(str(e))
        raise Exception("Falha ao enviar arquivo {filename}.")

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
            case 'select_partition':
                send_file(file_name, int(message))
    except Exception as e:
        udp.sendto(bytes('Servidor com erro.', 'ascii'), dest)
        
        print('erro: ' + str(e))
        
        if(str(e) != '[WinError 10040] Uma mensagem enviada em um soquete de datagrama era maior do que o buffer de mensagens internas ou excedia algum outro limite da rede, ou o buffer usado para receber um datagrama era menor do que o próprio datagrama'):
            raise Exception(str(e))
        
    

