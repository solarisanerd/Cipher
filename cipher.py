#server
import socket
import sys
import time
import os
from colorist import ColorHex

aqua = ColorHex("#2fd6c7")

host = "127.0.0.1"
port = 8052
buffersize = 200

def recieve():
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
        print(f'\n{data}')

        time.sleep(3)
        reply()

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

def main():
    while True:
        os.system('cls')
        print(rf'''{aqua}
 ______     __     ______   __  __     ______     ______   
/\  ___\   /\ \   /\  == \ /\ \_\ \   /\  ___\   /\  == \  
\ \ \____  \ \ \  \ \  _-/ \ \  __ \  \ \  __\   \ \  __<  
 \ \_____\  \ \_\  \ \_\    \ \_\ \_\  \ \_____\  \ \_\ \_\
  \/_____/   \/_/   \/_/     \/_/\/_/   \/_____/   \/_/ /_/
{aqua.OFF}

1. Start server
2. Exit
        ''')

        menu_options = int(input())

        if menu_options == 1:
            recieve()

        elif menu_options == 2:
            sys.exit()

        else:
            print('Invalid option')
            time.sleep(3)
            os.system('cls')
            continue

main()