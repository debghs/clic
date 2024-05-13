import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.user_color = None

    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == 'QUIT':
                    print("You have logged out successfully.")
                    break
                print(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_messages(self):
        while True:
            message = input("")
            if message.upper() == 'QUIT':
                self.send_message(message)
                break
            else:
                self.send_message(message)

    def start(self):
        self.connect()
        self.username = input("Enter your username>>>")
        self.send_message(self.username)

        self.user_color = self.client_socket.recv(1024).decode('utf-8')  # Receive color code

        receive_thread = threading.Thread(target=self.receive_messages)
        send_thread = threading.Thread(target=self.send_messages)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

        self.client_socket.close()

if __name__ == "__main__":
    client = ChatClient('localhost', 5555)
    client.start()
    	