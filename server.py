import socket
import threading
from queue import Queue

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.pending_messages = {}

    def handle_client(self, client_socket, username):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message == 'QUIT':
                    client_socket.send('QUIT'.encode('utf-8'))
                    del self.clients[username]
                    print(f"{username} has left")
                    self.broadcast(f'{username} has left the chat room!\n')
                    break
                elif message.startswith('@'):
                    recipient, msg_content = self.parse_private_message(message)
                    if recipient and msg_content:
                        self.send_private_message(username, recipient, msg_content)
                    else:
                        client_socket.send("Invalid private message format. Use '@username message'.\n".encode('utf-8'))
                else:
                    self.broadcast(username + ': ' + message)
            except Exception as e:
                print(f"Error handling client {username}: {e}")
                break

        client_socket.close()

    def broadcast(self, message):
        for client_socket in self.clients.values():
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting to a client: {e}")

    def parse_private_message(self, message):
        parts = message.split(' ', 1)
        if len(parts) == 2:
            recipient = parts[0][1:]
            msg_content = parts[1]
            return recipient, msg_content
        else:
            return None, None

    def send_private_message(self, sender, recipient, message):
        if recipient in self.clients:
            self.clients[recipient].send(f"{sender} (private): {message}".encode('utf-8'))
        else:
            if recipient not in self.pending_messages:
                self.pending_messages[recipient] = Queue()
            self.pending_messages[recipient].put((sender, message))

    def send_pending_messages(self, username):
        if username in self.pending_messages:
            while not self.pending_messages[username].empty():
                sender, message = self.pending_messages[username].get()
                self.clients[username].send(f"{sender} (offline): {message}".encode('utf-8'))
            del self.pending_messages[username]

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        while True:
            print(f"Server listening on {self.host}:{self.port}")
            client_socket, addr = self.server.accept()

            username = client_socket.recv(1024).decode('utf-8')

            print(f"Accepted connection from {username} at {addr}")
            self.broadcast(f'{username} has connected to the chat room')
            client_socket.send('you are now connected!\n'.encode('utf-8'))

            self.clients[username] = client_socket
            self.send_pending_messages(username)

            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, username))
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer('0.0.0.0', 5555)
    server.start()
