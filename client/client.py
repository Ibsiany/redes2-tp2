import socket

HOST = 'localhost'  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)

# Definindo uma porta para ser ouvida
udp.bind(('', 6000))

print('Socket UDP na porta 6000')

msg = input('Digite a mensagem: ')
udp.sendto(bytes(msg, 'ascii'), dest)

msg_confirmation, cliente = udp.recvfrom(1024)
print(cliente, msg_confirmation.decode('ascii'))

partition_length = input('Digite o tamanho das particoes: ')
udp.sendto(bytes(partition_length, 'ascii'), dest)

received_size, cliente = udp.recvfrom(1024)

array_size = int(received_size.decode('ascii'))

print(cliente, array_size)

array = []

for i in range(0, array_size):
    array.append('')

print(array)

values = ['']
while values[0] != 'end':
    payload, cliente = udp.recvfrom(1024)
    values = payload.decode('ascii').split('|', 1)
    if values[0] != 'end':
        if (int(values[0]) >= 0) & (int(values[0]) < array_size):
            array[int(values[0])] = values[1]

print(array)

fault_indexes = []

for i in range(len(array)):
    if array[i] == '':
        fault_indexes.append(i)

print(fault_indexes)

while len(fault_indexes) > 0:
    fault_msg = ''
    for i in range(len(fault_indexes)):
        fault_msg = fault_msg + str(fault_indexes[i])
        if i != len(fault_indexes) - 1:
            fault_msg = fault_msg + '|'

    udp.sendto(bytes(fault_msg, 'ascii'), dest)

    values = ['']

    while values[0] != 'fin?':
        payload, cliente = udp.recvfrom(1024)
        values = payload.decode('ascii').split('|')
        print(values)
        if values[0] != 'fin?':
            if (int(values[0]) >= 0) & (int(values[0]) < array_size):
                array[int(values[0])] = values[1]

    print(array)

    fault_indexes = []
    for i in range(len(array)):
        if array[i] == '':
            fault_indexes.append(i)



udp.sendto(bytes('fin', 'ascii'), dest)

udp.close()
print('Conexao finalizada')

mensagem = ''

for fragment in array:
    mensagem = mensagem + fragment

print("Mensagem recebida: ")
print(mensagem)
