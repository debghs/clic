import socket
import threading
from queue import Queue

# Server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5555

# Dictionary to store connected clients and their usernames
clients = {}
# Dictionary to store pending messages for offline users
pending_messages = {}


def handle_client(client_socket, username):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'QUIT':
                client_socket.send('QUIT'.encode('utf-8'))
                del clients[username]
                print(f"{username} has left")
                broadcast(f'{username} has left the chat room!\n')
                break
            elif message.startswith('@'):
                recipient, msg_content = parse_private_message(message)
                send_private_message(username, recipient, msg_content)
            else:
                broadcast(username + ': ' + message)
        except Exception as e:
            print(f"Error handling client {username}: {e}")
            break

    client_socket.close()


def broadcast(message):
    for client_socket in clients.values():
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")


def parse_private_message(message):
    # Extract recipient and message content from private message
    parts = message.split(' ', 1)
    recipient = parts[0][1:]
    msg_content = parts[1]
    return recipient, msg_content


def send_private_message(sender, recipient, message):
    if recipient in clients:
        # If the recipient is online, send the message immediately
        clients[recipient].send(f"{sender} (private): {message}".encode('utf-8'))
    else:
        # If the recipient is offline, queue the message
        if recipient not in pending_messages:
            pending_messages[recipient] = Queue()
        pending_messages[recipient].put((sender, message))


def send_pending_messages(username):
    if username in pending_messages:
        while not pending_messages[username].empty():
            sender, message = pending_messages[username].get()
            clients[username].send(f"{sender} (offline): {message}".encode('utf-8'))
        del pending_messages[username]


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    while True:
        print(f"Server listening on {HOST}:{PORT}")
        client_socket, addr = server.accept()

        # Get the username from the client
        username = client_socket.recv(1024).decode('utf-8')

        print(f"Accepted connection from {username} at {addr}")
        broadcast(f'{username} has connected to the chat room')
        client_socket.send('you are now connected!\n'.encode('utf-8'))

        # Add client to the dictionary
        clients[username] = client_socket

        # Send pending messages if any
        send_pending_messages(username)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()


if __name__ == "__main__":
    main()
