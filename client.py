#client
import socket
import time
import sys

host = "127.0.0.1"
port = 8052
buffersize = 200

def send():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((host, port))
        
        message = input("\nEnter message:\n\n")
        c.send(message.encode('ascii'))
        c.close()

        print('\nMessage sent\n\nWaiting for reply...')
        recieve()

def recieve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        print(f'\nServer is listening on {host}:{port}')
        
        #accept con request
        conn, addr = s.accept()
        print(f'\n{addr} is connected')

        #store recieved data & decode
        data = conn.recv(buffersize).decode(encoding='utf-8')
        print(f'\n{data}')

        time.sleep(3)
        
def reply():
    while True:
        reply = input('\nDo you want to reply (y/n):\n')
        if reply == "y":
            recieve()
        elif reply == "n":
            sys.exit()
        else:
            print('\nInvalid input\n')
            continue

send()