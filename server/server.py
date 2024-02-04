import math
import socket

HOST = ''  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
orig = (HOST, PORT)
udp.bind(orig)

dest = ('localhost', 6000)

print('Socket UDP na porta 5000')

msg, cliente = udp.recvfrom(1024)

sentence = msg.decode('ascii')

print(cliente, sentence)

udp.sendto(bytes('MSG RECEIVED', 'ascii'), dest)

partition_length, cliente = udp.recvfrom(1024)

partition_number = int(partition_length.decode('ascii'))

array_size = math.ceil(len(sentence) / partition_number)

udp.sendto(bytes(str(array_size), 'ascii'), dest)

array = []

for i in range(0, array_size):
    array.append(sentence[(i * partition_number):((i * partition_number) + partition_number)])

print(array)

for i in range(array_size):
    udp.sendto(bytes(str(i) + '|' + array[i], 'ascii'), dest)

udp.sendto(bytes('end', 'ascii'), dest)

indexes, cliente = udp.recvfrom(1024)

print(indexes.decode('ascii'))

while indexes.decode('ascii') != 'fin':
    indexes_array = indexes.decode('ascii').split('|')
    for i in indexes_array:
        print(i + '|' + array[int(i)])
        udp.sendto(bytes(i + '|' + array[int(i)], 'ascii'), dest)
    udp.sendto(bytes('fin?', 'ascii'), dest)
    indexes, cliente = udp.recvfrom(1024)

udp.close()
