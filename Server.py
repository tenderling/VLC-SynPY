import socket


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

sock.bind (('',9090))
clients = [] # Массив где храним адреса клиентов
print ('Start Server')

while 1 :
    try:
        data , addres = sock.recvfrom(1024)
        if data.decode('utf-8') == 'debug': print(clients)
        print ('{}:{} - {}'.format(addres[0], addres[1], data))
        # print (addres[0]+':'+addres[1] + data)

        if  addres not in clients : 
            clients.append(addres)# Если такого клиента нету , то добавить
        for client in clients :
            try:
                sock.sendto(data,client)
            except:
                continue
    except:
        continue