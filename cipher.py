# DO NOT JUDGE MY CODING

import sys
import time
import os
import socket
import threading
import datetime
import json
import subprocess
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
from colorist import ColorHex

aqua = ColorHex("#2fd6c7") #if you dont like aqua then cry about it. or just change the hex code idk
red = ColorHex("#ff0000")

#detect if os is windows with super complex quantum mechanics (importing modules)
try:
    import msvcrt
    is_windows = True
except ImportError:
    import tty
    import termios
    is_windows = False

config = {
    'host' : '0.0.0.0', #oH nO i LeAkEd mY Ip dOnT dOx Me
    'port' : 8052,
    'buffersize' : 4096,
    'max_clients' : 10,
    'log_file' : 'chat_history_log',
    'use_encryption' : True,
    'tor_enabled' : False,
    'tunnel_enabled' : False
}

#get keypresses
def get_key():
    if is_windows:
        key = msvcrt.getch()
        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H': return 'up'
            if key == b'P': return 'down'
        elif key == b'\r': return 'enter'
        elif key == b'\x1b': return 'esc'
        return key.decode('utf-8', errors='ignore')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(2)
                if ch2 == '[A': return 'up'
                if ch2 == '[B': return 'down'
                return 'esc'
            elif ch == '\r' or ch == '\n': return 'enter'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class server:
    def __init__(self):
        self.host = config['host']
        self.port = config['port']
        self.clients = {}
        self.client_count = 0
        self.running = True
        self.encryption_key = self.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.typing_status = {}

    def generate_key(self):
        password = b'change_this'
        salt = b'super_ultra_salty_cipher_salter' #tuff
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt, #ikr its crazy
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_message(self, message):
        if config['use_encryption']:
            return self.cipher.encrypt(message.encode()).decode()
        return message
        
    def decrypt_message(self, encrypted_msg):
        if config['use_encryption']:
            return self.cipher.decrypt(encrypted_msg.encode()).decode()
        return encrypted_msg

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p') 
        with open(config['log_file'], 'a', encoding='utf8') as f:
            f.write(f'[{timestamp}] {message}\n')

    def broadcast(self, message, sender_conn=None, sender_name='Server', msg_type='message'):
        timestamp = datetime.datetime.now().strftime('%I:%M:%S %p') #why is does the hour have to be %I?

        if msg_type == 'message':
            formatted_msg = f'[{timestamp}] {sender_name}: {message}'
            self.log_message(formatted_msg)
        elif msg_type == 'typing':
            formatted_msg = f'typing:{sender_name}'
        elif msg_type == 'stop_typing':
            formatted_msg = f'stop_typing:{sender_name}'
        else:
            formatted_msg = message

        for client_conn, client_info in list(self.clients.items()):
            if client_conn != sender_conn:
                try:
                    encrypted = self.encrypt_message(formatted_msg)
                    client_conn.send(encrypted.encode('utf-8'))
                except:
                    self.remove_client(client_conn)
                #i hope this thing actually works
    
    def handle_client(self, conn, addr):
        print(f'{aqua}[+] {addr} connected{aqua.OFF}')

        try:
            #hopefully there wont be heaps of weird ass usernames
            conn.send(self.encrypt_message('Enter username').encode('utf-8'))
            username_data = conn.recv(config['buffersize']).decode('utf-8')
            username = self.decrypt_message(username_data)

            self.clients[conn] = {'username': username, 'addr': addr}
            self.typing_status[username] = False
            self.broadcast(f'{username} joined', sender_name='System')
            print(f'{aqua}[+] {username} ({addr}) joined{aqua.OFF}')

            #user list
            user_list = ', '.join([info['username'] for info in self.clients.values()])
            conn.send(self.encrypt_message(f'Users_online:{user_list}').encode('utf-8'))

            while self.running:
                data = conn.recv(config['buffersize']).decode('utf-8')
                if not data:
                    break

                decrypted = self.decrypt_message(data)

                #typing indicators
                if decrypted == 'typing_start':
                    self.typing_status[username] = True
                    self.broadcast('', sender_conn=conn, sender_name=username, msg_type='typing') #its 1:38am right now, love life
                    continue
                elif decrypted == 'typing_stop':
                    self.typing_status[username] = False
                    self.broadcast('', sender_conn=conn, sender_name=username, msg_type='stop_typing') #idk if this makes 
                    continue
                
                #this is suppose to make it stop typing when a message is sent but idk if it works
                if username in self.typing_status:
                    self.typing_status[username] = False
                    self.broadcast('', sender_conn=conn, sender_name=username, msg_type='stop_typing')

                #and idk what this part does, i just hope it does something
                if decrypted.startswith('/'):
                    self.handle_command(decrypted, conn, username)
                else:
                    print(f'{aqua}[{username}]: {decrypted}{aqua.OFF}')
                    self.broadcast(decrypted, sender_conn=conn, sender_name=username)
            
        except Exception as e:
            print(f'{red}[-] Error with {addr}: {e}{red.OFF}')
        finally:
            self.remove_client(conn)
        
    def handle_command(self, command, conn, username):
        parts = command.split(' ', 1)
        cmd = parts[0].lower()

        if cmd == '/quit':
            conn.send(self.encrypt_message('disconnect').encode('utf-8'))
            self.remove_client(conn)
        
        elif cmd == '/users':
            user_list = ', '.join([info['username'] for info in self.clients.values()])
            conn.send(self.encrypt_message(f'Online users: {user_list}').encode('utf-8'))

        elif cmd == '/help':
            help_text = '''
Commands:
/quit - Disconnect from server
/users - List online users
/whisper <user> <msg> - Send private message
/clear - Clear your screen
/help - Show this help
'''
            conn.send(self.encrypt_message(help_text).encode('utf-8'))
        
        elif cmd == '/whisper' and len(parts) > 1:
            try:
                target_user, msg = parts[1].split(' ', 1) #wish i was getting paid for this
                target_conn = None
                for c, info in self.clients.items():
                    if info['username'] == target_user:
                        target_conn = c
                        break
            
                if target_conn:
                    timestamp = datetime.datetime.now().strftime('%I:%M:%S %p')
                    whisper_msg = f'[{timestamp}] (Whisper from {username}): {msg}'
                    target_conn.send(self.encrypt_message(whisper_msg).encode('utf-8'))
                    conn.send(self.encrypt_message(f'Whisper sent to {target_user}').encode('utf-8'))
                else:
                    conn.send(self.encrypt_message(f'User {target_user} not found').encode('utf-8'))
            
            except:
                conn.send(self.encrypt_message('Usage: /whisper <username> <message>').encode('utf-8'))
        
        elif cmd == '/clear':
            conn.send(self.encrypt_message('clear_screen').encode('utf-8'))
    
    def remove_client(self, conn):
        if conn in self.clients:
            username = self.clients[conn]['username']
            addr = self.clients[conn]['addr']
            del self.clients[conn]
            if username in self.typing_status:
                del self.typing_status[username]
            self.broadcast(f'{username} left the chat', sender_name='System')
            print(f'{red}[-] {username} ({addr}) disconnected{red.OFF}')
            try:
                conn.close()
            except:
                pass
        
    def start(self):
        #AF_INET = IPv4 & SOCK_STREAM = TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(config['max_clients'])

            os.system('cls' if os.name == 'nt' else 'clear')
            logo()
            print(f'\n{aqua}[+] Server listening on {self.host}:{self.port}{aqua.OFF}')
            print(f'{aqua}[*] Encryption: {"Enabled" if config["use_encryption"] else "Disabled"}{aqua.OFF}')
            print(f'{aqua}[*] Max clients: {config["max_clients"]}{aqua.OFF}')
            print(f'{aqua}[*] Logs: {config["log_file"]}{aqua.OFF}\n')
            
            if config['tunnel_enabled']:
                print(f'{aqua}[*] Tunneling Instructions:{aqua.OFF}')
                print(f'{aqua}    → LocalTunnel: lt --port {self.port}{aqua.OFF}')
                print(f'{aqua}    → Serveo: ssh -R 80:localhost:{self.port} serveo.net{aqua.OFF}')
                print(f'{aqua}    → Cloudflare: cloudflared tunnel --url localhost:{self.port}{aqua.OFF}\n')
            
            if config['tor_enabled']:
                print(f'{aqua}[*] Tor Service: Install stem (pip install stem){aqua.OFF}\n')

            try:
                while self.running:
                    conn, addr = s.accept()
                    if len(self.clients) >= config['max_clients']:
                        conn.send(self.encrypt_message('Server full').encode('utf-8'))
                        conn.close()
                        continue
                    
                    client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                    client_thread.daemon = True
                    client_thread.start()
            except KeyboardInterrupt:
                print(f'\n{red}[!] Server shutting down...{red.OFF}')
                self.running = False


class client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
        self.username = ""
        self.encryption_key = self.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.typing_users = set()
        self.current_input = ""
        self.is_typing = False
        self.last_typing_time = 0
        
    def generate_key(self):
        password = b'change_this'
        salt = b'super_ultra_salty_cipher_salter'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_message(self, message):
        if config['use_encryption']:
            return self.cipher.encrypt(message.encode()).decode()
        return message
    
    def decrypt_message(self, encrypted_msg):
        if config['use_encryption']:
            return self.cipher.decrypt(encrypted_msg.encode()).decode()
        return encrypted_msg
    
    def show_typing_indicator(self):
        if self.typing_users:
            users = ", ".join(self.typing_users)
            return f'{aqua}💬 {users} {"is" if len(self.typing_users) == 1 else "are"} typing...{aqua.OFF}'
        return ""
    
    def receive_messages(self, sock):
        while self.running:
            try:
                data = sock.recv(config['buffersize']).decode('utf-8')
                if not data:
                    break
                
                decrypted = self.decrypt_message(data)
                
                if decrypted == 'disconnect':
                    self.running = False
                    break
                elif decrypted == 'clear_screen':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    logo()
                elif decrypted.startswith('Users_online:'):
                    users = decrypted.replace('Users_online:', '')
                    print(f'\n{aqua}[Online]: {users}{aqua.OFF}\n')
                elif decrypted.startswith('typing:'):
                    user = decrypted.replace('typing:', '')
                    self.typing_users.add(user)
                    print(f'\r{self.show_typing_indicator()}', end='', flush=True)
                elif decrypted.startswith('stop_typing:'):
                    user = decrypted.replace('stop_typing:', '')
                    self.typing_users.discard(user)
                    if not self.typing_users:
                        print(f'\r{" " * 80}\r', end='', flush=True)
                        print(f'{aqua}[{self.username}]: {aqua.OFF}{self.current_input}', end='', flush=True)
                elif decrypted != 'Enter username':
                    print(f'\n{decrypted}')
                    typing_indicator = self.show_typing_indicator()
                    if typing_indicator:
                        print(typing_indicator)
                    print(f'{aqua}[{self.username}]: {aqua.OFF}{self.current_input}', end='', flush=True)
                    
            except Exception as e:
                if self.running:
                    print(f'\n{red}[-] Connection error: {e}{red.OFF}')
                break
        
        print(f'\n{red}[!] Disconnected from server{red.OFF}')
    
    def send_typing_status(self, sock, typing):
        current_time = time.time()
        if typing and not self.is_typing:
            sock.send(self.encrypt_message('typing_start').encode('utf-8'))
            self.is_typing = True
            self.last_typing_time = current_time
        elif not typing and self.is_typing:
            if current_time - self.last_typing_time > 1:
                sock.send(self.encrypt_message('typing_stop').encode('utf-8'))
                self.is_typing = False
    
    def start(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                
                os.system('cls' if os.name == 'nt' else 'clear')
                logo()
                print(f'{aqua}[+] Connected to {self.host}:{self.port}{aqua.OFF}\n')
                
                username_prompt = sock.recv(config['buffersize']).decode('utf-8')
                self.username = input('Enter username: ') #dont make the username too wild please
                sock.send(self.encrypt_message(self.username).encode('utf-8'))

                receive_thread = threading.Thread(target=self.receive_messages, args=(sock,))
                receive_thread.daemon = True
                receive_thread.start()

                time.sleep(0.5)
                print(f'\n{aqua}Type /help for commands{aqua.OFF}\n')

                while self.running:
                    message = input(f'{aqua}[{self.username}]: {aqua.OFF}')
                    self.current_input = ''

                    if not self.running:
                        break
                    
                    if self.is_typing:
                        sock.send(self.encrypt_message('typing_stop').encode('utf-8'))
                        self.is_typing = False

                    if message.strip():
                        encrypted = self.encrypt_message(message)
                        sock.send(encrypted.encode('utf-8'))

                        if message == '/quit':
                            self.running = False
                            break
        
        except ConnectionRefusedError:
            print(f'{red}[-] Cannot connect to server. Is it running?{red.OFF}') #pro tip, running it allows you to connect to it
        except Exception as e:
            print(f'{red}[-] Error: {e}{red.OFF}')

def logo():
    print(rf'''{aqua}
  ______     __     ______   __  __     ______     ______   
 /\  ___\   /\ \   /\  == \ /\ \_\ \   /\  ___\   /\  == \  
 \ \ \____  \ \ \  \ \  _-/ \ \  __ \  \ \  __\   \ \  __<  
  \ \_____\  \ \_\  \ \_\    \ \_\ \_\  \ \_____\  \ \_\ \_\
   \/_____/   \/_/   \/_/     \/_/\/_/   \/_____/   \/_/ /_/
{aqua.OFF}''') #super tuff ascii art

#ok im not gonna lie, i got no idea how this interactive menu stuff works i just looked all of it up and hope it works
def draw_menu(options, selected, title='CIPHER'):
    os.system('cls' if os.name == 'nt' else 'clear')
    logo()
    print(f'\n{aqua}{"="*60}')
    print(f'{title:^60}')
    print(f'{"="*60}{aqua.OFF}\n')

    for i, option in enumerate(options):
        if i == selected:
            print(f'{aqua}  ▶ {option}{aqua.OFF}')
        else:
            print(f'    {option}')
        
    print(f'\n{aqua}Use up and down arrow keys to navigate, Enter to select, & ESC to go back{aqua.OFF}')

#please dont ask me how this works, ask ai or something
def interactive_menu(options, title='CIPHER'):
    selected = 0

    while True:
        draw_menu(options, selected, title)

        key = get_key()

        if key == 'up':
            selected = (selected - 1) % len(options)
        elif key == 'down':
            selected = (selected + 1) % len(options)
        elif key == 'enter':
            return selected
        elif key == 'esc':
            return -1

def start_tunnel(tunnel_type, port):
    """Start tunneling service based on selection"""
    try:
        if tunnel_type == 'localtunnel':
            print(f'\n{aqua}[*] Starting LocalTunnel on port {port}...{aqua.OFF}')
            print(f'{aqua}[*] Make sure you have LocalTunnel installed: npm install -g localtunnel{aqua.OFF}\n')
            process = subprocess.Popen(['lt', '--port', str(port)], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            time.sleep(2)
            print(f'{aqua}[*] LocalTunnel started! Check above for your URL{aqua.OFF}')
            print(f'{aqua}[*] Share the URL with your friends (without https://){aqua.OFF}\n')
            return process
            
        elif tunnel_type == 'serveo':
            print(f'\n{aqua}[*] Starting Serveo tunnel on port {port}...{aqua.OFF}')
            print(f'{aqua}[*] No installation needed!{aqua.OFF}\n')
            process = subprocess.Popen(['ssh', '-R', f'80:localhost:{port}', 'serveo.net'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            time.sleep(2)
            print(f'{aqua}[*] Serveo tunnel started! Check above for your URL{aqua.OFF}\n')
            return process
            
        elif tunnel_type == 'cloudflare':
            print(f'\n{aqua}[*] Starting Cloudflare Tunnel on port {port}...{aqua.OFF}')
            print(f'{aqua}[*] Make sure cloudflared is installed{aqua.OFF}\n')
            process = subprocess.Popen(['cloudflared', 'tunnel', '--url', f'tcp://localhost:{port}'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            time.sleep(2)
            print(f'{aqua}[*] Cloudflare Tunnel started! Check above for your URL{aqua.OFF}\n')
            return process
            
        elif tunnel_type == 'pinggy':
            print(f'\n{aqua}[*] Starting Pinggy tunnel on port {port}...{aqua.OFF}')
            print(f'{aqua}[*] No installation needed!{aqua.OFF}\n')
            process = subprocess.Popen(['ssh', '-p', '443', '-R', f'0:localhost:{port}', 'a.pinggy.io'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            time.sleep(2)
            print(f'{aqua}[*] Pinggy tunnel started! Check above for your URL{aqua.OFF}\n')
            return process
            
        elif tunnel_type == 'ngrok':
            print(f'\n{aqua}[*] Starting Ngrok on port {port}...{aqua.OFF}')
            print(f'{aqua}[*] Make sure ngrok is installed and authenticated{aqua.OFF}\n')
            process = subprocess.Popen(['ngrok', 'tcp', str(port)],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            time.sleep(2)
            print(f'{aqua}[*] Ngrok started! Check ngrok dashboard for your URL{aqua.OFF}\n')
            return process
            
    except FileNotFoundError:
        print(f'{red}[-] Error: {tunnel_type} command not found. Please install it first.{red.OFF}')
        return None
    except Exception as e:
        print(f'{red}[-] Error starting tunnel: {e}{red.OFF}')
        return None


def host_menu():
    """Menu for hosting options with tunneling"""
    while True:
        options = [
            'Host Locally (No Tunnel)',
            'Host with LocalTunnel',
            'Host with Serveo',
            'Host with Cloudflare Tunnel',
            'Back to Main Menu'
        ]
        
        choice = interactive_menu(options, 'HOST SERVER')
        
        if choice == -1 or choice == 4:
            break
            
        elif choice == 0:
            # Local hosting only
            s = server()
            s.start()
            input('\nPress enter to return to menu')
            
        else:
            # Hosting with tunnel
            tunnel_types = ['', 'localtunnel', 'serveo', 'cloudflare']
            tunnel_type = tunnel_types[choice]
            
            os.system('cls' if os.name == 'nt' else 'clear')
            logo()
            print(f'\n{aqua}Starting server with {tunnel_type.title()}...{aqua.OFF}\n')
            
            # Start tunnel in background
            tunnel_process = start_tunnel(tunnel_type, config['port'])
            
            if tunnel_process:
                print(f'{aqua}[*] Tunnel is running in the background{aqua.OFF}')
                print(f'{aqua}[*] Starting Cipher server...{aqua.OFF}\n')
                
                # Start server
                s = server()
                try:
                    s.start()
                except KeyboardInterrupt:
                    print(f'\n{red}[!] Shutting down...{red.OFF}')
                finally:
                    # Kill tunnel process
                    try:
                        tunnel_process.terminate()
                        tunnel_process.wait(timeout=5)
                    except:
                        tunnel_process.kill()
                    print(f'{red}[!] Tunnel stopped{red.OFF}')
                
                input('\nPress enter to return to menu')
            else:
                print(f'{red}[-] Failed to start tunnel{red.OFF}')
                input('\nPress enter to return to menu')


def settings_menu():
    while True:
        options = [
            f'Port: {config["port"]}',
            f'Max Clients: {config["max_clients"]}',
            f'Encryption: {"ON" if config["use_encryption"] else "OFF"}',
            f'Tor Service: {"ON" if config["tor_enabled"] else "OFF"}',
            f'Tunneling Info: {"ON" if config["tunnel_enabled"] else "OFF"}',
            'Back to Main Menu'
        ]

        choice = interactive_menu(options, 'settings')

        if choice == -1 or choice == 5:
            break
        elif choice == 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            logo()
            port = input(f'\n{aqua}Enter new port (current: {config["port"]}): {aqua.OFF}')
            if port.isdigit():
                config['port'] = int(port)
        elif choice == 1:
            os.system('cls' if os.name == 'nt' else 'clear') #whats the difference between snow men and snow women, snow balls, just laugh please
            logo()
            max_clients = input(f'\n{aqua}Enter max clients (current: {config["max_clients"]}): {aqua.OFF}')
            if max_clients.isdigit():
                config['max_clients'] = int(max_clients)
        elif choice == 2:
            config['use_encryption'] = not config['use_encryption']
        elif choice == 3:
            config['tor_enabled'] = not config['tor_enabled']
        elif choice == 4:
            config['tunnel_enabled'] = not config['tunnel_enabled']


def main():
        while True:
            menu_options = [
                'Host cipher server',
                'Connect to server',
                'Settings',
                'Exit'
            ]

            choice = interactive_menu(menu_options)

            if choice == -1 or choice == 3:
                os.system('cls' if os.name == 'nt' else 'clear')
                logo()
                print(f'\n{aqua}Thanks for using cipher{aqua.OFF}\n')
                sys.exit(0)

            elif choice == 0:
                host_menu()

            elif choice == 1:
                os.system('cls' if os.name == 'nt' else 'clear')
                logo()
                host = input(f'\n{aqua}Enter server ip/url (default: localhost): {aqua.OFF}').strip() or 'localhost'
                port = input(f'{aqua}Enter port (default: 8052): {aqua.OFF}').strip() or '8052'
                c = client(host, int(port))
                c.start()
                input('\nPress enter to return to menu')
            
            elif choice == 2:
                settings_menu()

main()