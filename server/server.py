import socket
import os
import base64

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
        
        raise Exception('Arquivo nao encontrado.')

    udp.sendto(bytes('ENVIANDO O ARQUIVO: ' + filename, 'ascii'), dest)
    send_file(filename);

def send_file(filename): # Função para enviar o arquivo selecionado
    try:
        with open(diretorio+"/"+filename, "rb") as arquivo:
            conteudo_arquivo = arquivo.read()
            arquivo_codificado = base64.b64encode(conteudo_arquivo)
            
            file = arquivo_codificado.decode("utf-8")
            
            length = len(file)
            tam = len(file)
            
            initial = 0
            final = 1023
            
            while length > 0:
                udp.sendto(bytes(file[initial:final], 'ascii'), dest)
                initial = final
                if(length < 1024):
                    final = final + length
                else:
                    final = final+1024
                if(length <= 1024):
                    length = length - length
                else:
                    length = length - 1024
                
                print('PACOTE ENVIADO')
                
            print(tam)
            print('Acabou no server.')
            udp.sendto(bytes('FIM', 'ascii'), dest)
            print('caralho')
                
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
    except Exception as e:
        udp.sendto(bytes('Servidor com erro.', 'ascii'), dest)
        
        print('erro: ' + str(e))
        
        if(str(e) != '[WinError 10040] Uma mensagem enviada em um soquete de datagrama era maior do que o buffer de mensagens internas ou excedia algum outro limite da rede, ou o buffer usado para receber um datagrama era menor do que o próprio datagrama'):
            raise Exception(str(e))
        
    

