#client
import socket

host = "127.0.0.1"
port = 8052

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
    c.connect((host, port))
    
    message = input("\nEnter message:\n\n")
    c.send(message.encode('ascii'))
    c.close