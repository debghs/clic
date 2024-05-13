import socket
import threading
from queue import Queue
import random

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.pending_messages = {}
        self.user_colors = {}

    def handle_client(self, client_socket, username):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message == 'QUIT':
                    client_socket.send('QUIT'.encode('utf-8'))
                    del self.clients[username]
                    del self.user_colors[username]  # Remove color mapping
                    print(f"{username} has left")
                    self.broadcast("",f'{username} has left the chat room!\n')
                    break
                elif message.startswith('@'):
                    recipient, msg_content = self.parse_private_message(message)
                    self.send_private_message(username, recipient, msg_content)
                else:
                    self.broadcast(username, message)
            except Exception as e:
                print(f"Error handling client {username}: {e}")
                break

        client_socket.close()

    def broadcast(self, sender, message):
        sender_color = self.user_colors.get(sender, "")  # Get sender's color code
        for recipient, client_socket in self.clients.items():
            try:
                recipient_color = self.user_colors.get(recipient, "")  # Get recipient's color code
                client_socket.send((sender_color + sender + ": " + message + "\033[0m\n").encode('utf-8'))  # Reset color after message
            except Exception as e:
                print(f"Error broadcasting to {recipient}: {e}")

    def parse_private_message(self, message):
        parts = message.split(' ', 1)
        recipient = parts[0][1:]
        msg_content = parts[1]
        return recipient, msg_content


    def send_private_message(self, sender, recipient, message):
        sender_color = self.user_colors.get(sender, "")  # Get sender's color code
        if recipient in self.clients:
            recipient_color = self.user_colors.get(recipient, "")  # Get recipient's color code
            self.clients[recipient].send((sender_color + f"{sender} (private): {message}" + "\033[0m").encode('utf-8'))  # Reset color after message
        else:
            if recipient not in self.pending_messages:
                self.pending_messages[recipient] = Queue()
            self.pending_messages[recipient].put((sender, message))


    def send_pending_messages(self, username):
        if username in self.pending_messages:
            sender_color = self.user_colors.get(username, "")  # Get sender's color code
            while not self.pending_messages[username].empty():
                sender, message = self.pending_messages[username].get()
                recipient_color = self.user_colors.get(sender, "")  # Get recipient's color code
                self.clients[username].send((recipient_color + f"{sender} (offline): {message}" + "\033[0m").encode('utf-8'))  # Reset color after message
            del self.pending_messages[username]


    def assign_color(self, username):
        if username not in self.user_colors:
            # Generate a unique random color for the user
            color = f"\033[38;5;{random.randint(16, 255)}m"
            self.user_colors[username] = color

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        while True:
            print(f"Server listening on {self.host}:{self.port}")
            client_socket, addr = self.server.accept()

            username = client_socket.recv(1024).decode('utf-8')
            self.assign_color(username)  # Assign a color to the user

            print(f"Accepted connection from {username} at {addr}")
            self.broadcast(f'{username} has connected to the chat room', "")  # Broadcast without sender color
            client_socket.send((self.user_colors[username] + 'you are now connected!\n\033[0m').encode('utf-8'))  # Send color to client

            self.clients[username] = client_socket
            self.send_pending_messages(username)

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, username))
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer('0.0.0.0', 5555)
    server.start()
