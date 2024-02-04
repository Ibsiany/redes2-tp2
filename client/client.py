import socket

HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)

# Definindo uma porta para ser ouvida
udp.bind(('', 6000))

print('Socket UDP na porta 6000')

password = input('Digite a senha: ')
udp.sendto(bytes('password|' + password, 'ascii'), dest)

msg_confirmation, cliente = udp.recvfrom(1024)
print(cliente, msg_confirmation.decode('ascii'))

if(msg_confirmation.decode('ascii') == 'SENHA INCORRETA'):
    print('Conexao finalizada, senha incorreta!')
    udp.close()
else:
    try:
        msg_list, cliente = udp.recvfrom(1024)
        print(cliente, msg_list.decode('ascii'))

        arquivo = input('Digite o arquivo desejado: ')
        udp.sendto(bytes('select_file|'+arquivo, 'ascii'), dest)

        msg_arquivo, cliente = udp.recvfrom(1024)
        print(cliente, msg_arquivo.decode('ascii'))

        

    except Exception as e:
        print('erro errado: ' + str(e))

