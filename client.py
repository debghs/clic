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
        self.input_window = None
        self.message_window = None

    def connect(self):
        try:
            self.client_socket.connect((self.server_host, self.server_port))
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.running = False

    def send_message(self, message):
        try:
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                if message == 'QUIT':
                    self.messages.append("You have logged out successfully.")
                    self.running = False
                    break
                self.messages.append(message)
                if self.message_window:
                    self.display_messages(self.message_window)
                    self.message_window.refresh()
            except Exception as e:
                self.messages.append(f"Error receiving message: {e}")
                self.running = False
                break

    def start(self, stdscr):
        self.connect()
        if not self.running:
            return

        self.setup_curses(stdscr)

        self.username = self.get_username_input(stdscr, "Enter your username: ")
        self.send_message(self.username)

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        input_thread = threading.Thread(target=self.input_handler)
        input_thread.daemon = True
        input_thread.start()

        while self.running:
            self.update_windows()
            curses.napms(100)

        receive_thread.join()
        self.client_socket.close()

    def setup_curses(self, stdscr):
        curses.curs_set(0)
        h, w = stdscr.getmaxyx()
        self.message_window = stdscr.subwin(h - 1, w, 0, 0)
        self.input_window = stdscr.subwin(1, w, h - 1, 0)
        self.input_window.keypad(True)
        self.input_window.addstr(0, 0, "Enter message: ")
        self.input_window.refresh()

    def update_windows(self):
        self.display_messages(self.message_window)
        self.input_window.refresh()

    def display_messages(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        msg_display_height = h - 1
        for idx, message in enumerate(self.messages[-msg_display_height:]):
            stdscr.addstr(idx, 0, message)

    def input_handler(self):
        while self.running:
            message = self.get_message_input(self.input_window)
            if message.upper() == 'QUIT':
                self.send_message(message)
                self.running = False
                break
            else:
                self.send_message(message)

    def get_username_input(self, stdscr, prompt):
        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        curses.echo()
        input_str = stdscr.getstr().decode('utf-8').strip()
        curses.noecho()
        return input_str

    def get_message_input(self, stdscr):
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter message: ")
        stdscr.refresh()
        curses.echo()
        input_str = stdscr.getstr().decode('utf-8').strip()
        curses.noecho()
        return input_str

def main(stdscr):
    client = ChatClient('localhost', 5555)
    client.start(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
