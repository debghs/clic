import socket
import threading

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5555

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'QUIT':
                print("you have logged out, successfully.")
                break
            print(message)
        except Exception as e:
            print(f"error receiving message: {e}")
            break

# Function to send messages to the server
def send_messages(client_socket):
    while True:
        message = input("")
        if message.upper() == 'QUIT':
            client_socket.send(message.encode('utf-8'))
            break
        else:
            client_socket.send(message.encode('utf-8'))

# Main function to establish the connection
def main():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Get the username from the user
    username = input("Enter your username>>>")
    client_socket.send(username.encode('utf-8'))

    # Start threads for sending and receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    # Close the connection when the threads finish
    client_socket.close()

if __name__ == "__main__":
    main()
