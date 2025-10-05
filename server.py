#server
import socket

host = "127.0.0.1"
port = 8052
buffersize = 200

#AF_INET = IPv4 & SOCK_STREAM = TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    print(f'\nServer is listening on {host}:{port}')
    
    #accept con request
    conn, addr = s.accept()
    print(f'\n{addr} is connected')

    #store recieved data & decode
    data = conn.recv(buffersize).decode(encoding='utf-8')
    print(f'\n{data}\n')
