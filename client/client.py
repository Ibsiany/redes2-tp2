import socket
import os
import base64
    
HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
diretorio = './files'


def receber_arquivo(filename):
    buffer = []
    
    base64_decode = ''
    
    while base64_decode != 'FIM':
        base64_string, cliente = udp.recvfrom(5 * 1024)
        
        base64_decode = base64_string.decode('ascii')
        
        if(base64_decode != 'FIM'):
            buffer.append(base64_decode)
            print('PACOTE RECEBIDO')
        else:
            print('FIM')
            
    try:
        caminho_completo = os.path.join(diretorio, filename)
        
        with open(caminho_completo, "wb") as arquivo:
            bufferIsString = ''.join(buffer)
            
            arquivo_decodificado = base64.b64decode(bufferIsString)
            arquivo.write(arquivo_decodificado)

        print ("Arquivo salvo em: " + caminho_completo)
    except Exception as e:
        raise Exception("Erro ao salvar o arquivo:"+str(e))

# Definindo uma porta para ser ouvida
udp.bind(('', 6000))

print('Socket UDP na porta 6000')

password = input('Digite a senha: ')
udp.sendto(bytes('password|' + password, 'ascii'), dest)

msg_confirmation, cliente = udp.recvfrom(5 * 1024 * 1024)
print(cliente, msg_confirmation.decode('ascii'))

if(msg_confirmation.decode('ascii') == 'SENHA INCORRETA'):
    print('Conexao finalizada, senha incorreta!')
    udp.close()
else:
    try:
        msg_list, cliente = udp.recvfrom(5 * 1024 * 1024)
        print(cliente, msg_list.decode('ascii'))

        arquivo = input('Digite o arquivo desejado: ')
        udp.sendto(bytes('select_file|'+arquivo, 'ascii'), dest)

        msg_arquivo, cliente = udp.recvfrom(5 * 1024 * 1024)
        print(cliente, msg_arquivo.decode('ascii'))
        
        receber_arquivo(arquivo)

    except Exception as e:
        print('Erro interno: ' + str(e))


