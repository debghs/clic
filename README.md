# clic

clic (command line interface for chatting) is a simple chat application that allows multiple clients to connect to a server and communicate with each other in real-time using TCP sockets.

## Features

- Multiple clients can connect to the server simultaneously.
- Clients can send messages to the chat room, which will be broadcasted to all other connected clients.
- Private messages can be sent between clients by mentioning the recipient's username.
- Offline messages are stored and delivered to the recipient once they reconnect to the server.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/debghs/clic.git
    ```

2. Navigate to the project directory:

    ```
    cd clic
    ```

3. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

### Server

To start the server, run the following command:

```
python server.py
```

The server will start listening for incoming connections on the specified host and port.

### Client
To connect to the server as a client, run the following command:

```
python client.py
```
Enter your username.
Start sending and recieving messages.

## Commands
- To send a message to the chat room, simply type your message and press Enter.
- To send a private message to a specific user, use the following format: ``` @ "username" "message" ```
- To log out and quit the chat application, type ```QUIT``` and press Enter.
