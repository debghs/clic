import socket
import threading
import curses

class ChatClient:
    def __init__(self, host, port):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.messages = []
        self.running = True

    def connect(self):
        self.client_socket.connect((self.server_host, self.server_port))

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                if message == 'QUIT':
                    self.messages.append("You have logged out successfully.")
                    break
                self.messages.append(message)
            except Exception as e:
                self.messages.append(f"Error receiving message: {e}")
                break

    def start(self, stdscr):
        self.connect()
        self.username = self.get_user_input(stdscr, "Enter your username: ")
        self.send_message(self.username)

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        try:
            while True:
                self.display_messages(stdscr)
                stdscr.refresh()
                curses.napms(100)
                message = self.get_user_input(stdscr, "Enter message: ")
                if message.upper() == 'QUIT':
                    self.send_message(message)
                    self.running = False
                    break
                else:
                    self.send_message(message)
        finally:
            self.running = False
            receive_thread.join()
            self.client_socket.close()

    def display_messages(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        msg_display_height = h - 2
        for idx, message in enumerate(self.messages[-msg_display_height:]):
            stdscr.addstr(idx, 0, message)

    def get_user_input(self, stdscr, prompt):
        h, w = stdscr.getmaxyx()
        input_win = curses.newwin(1, w, h-1, 0)
        input_win.addstr(0, 0, prompt)
        input_win.refresh()
        input_str = ""
        curses.echo()
        while True:
            key = input_win.getch()
            if key == curses.KEY_ENTER or key == 10:
                break
            elif key == curses.KEY_BACKSPACE or key == 127:
                if len(input_str) > 0:
                    input_str = input_str[:-1]
                    input_win.clear()
                    input_win.addstr(0, 0, prompt + input_str)
                    input_win.refresh()
            else:
                input_str += chr(key)
                input_win.addstr(0, 0, prompt + input_str)
                input_win.refresh()
        curses.noecho()
        return input_str

def main(stdscr):
    client = ChatClient('localhost', 5555)
    client.start(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
