import argparse  # передача ключей значений
import socket
import shlex  # лексический анализ
import subprocess  # выполнение команд линукс из скрипта
import sys
import textwrap  # перенос и заполенние текста
import threading  # работа с потоками


def printBanner():
        print("|\    |      ______   _________     ______          __        _______              ")
        print("| \   |      |            |              |         /  \          |        |        ")
        print("|  \  |      |____        |         _____|        /    \         |        |        ")
        print("|   \ |      |            |         |            /______\        |        |        ")
        print("|    \|      |_____       |         |_____      /        \    ___|___     |_____   ")
        print("\n")
        print("\n")
        print('                                                                     [*] Net2tail version 0.1.4')
        print('                                                                     [*] Designed by AmaSus01')
        print('                                                                     [*] github.com/AmaSus01')
        print("\n")
        print("Print 'python3 net2ail.py --help' in your console for more information how to use this framework")

class Net2ail:
    def __init__(self, args, buffer=None):  # инициализируем неттаил объектов аргументамы из командной строки и буфера
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем объект сокет
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):  # точка входа для управления объектом неттаил выполняет 2 метода,
        if self.args.listen:
            self.listen()  # слушаем
        else:
            self.send()  # в протвином случаи отправляем

    def send(self):  # функция на метод отправки
        self.socket.connect((self.args.target, self.args.port))  # connected to the target and port
        if self.buffer:
            self.socket.send(self.buffer)  # если у нас есть буффер мы делаем отправку на таргет

        try:  # условие для Ctrl-C
            while True:  # loop дя получения даты от таргета
                get_len = 1
                response = ''
                while get_len:
                    data = self.socket.recv(4096)
                    get_len = len(data)
                    response += data.decode()
                    if get_len < 4096:
                        break  # если даты больше нет то выходим из loop
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())  # иначе выводим дату и делаем паузу для интерактивного ввода и продолжаем loop
        except KeyboardInterrupt:  # условие на прерыанеи с клавиатуры, закрываем сокет
            print('User terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))  # передача подключенного сокета методу handle
            client_thread.start()

# выполенние команды строкового аргумента который он получает: выполнить команду, загрузить файл, запустить шел
    def handle(self, client_socket):
        if self.args.execute:  # метод handle передает эту команду функции execute и отправляет вывод обратно в сокет.
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:  # загрузка файла и вход в loop до тех пор пока он не перестанет получать дату
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
                message = f'Saved file {self.args.upload}'
                client_socket.send(message.encode())

        # если был создан шел и выполнение команды
        elif self.args.command:
            print('Someone in system!!! ')
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP:#> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f' server killed{e}')
                    self.socket.close()
                    sys.exit()


# run a command on the local os and return output form command
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


if __name__ == '__main__':
    # интерфейс команд
    printBanner()
    parser = argparse.ArgumentParser(description='Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=textwrap.dedent('''Example:
        net2ail.py -t 192.168.1.108 -p 5555 -l -c #command shell
        net2ail.py -t 192.168.1.108 -p 5555 -l -u=example.txt # upload to file
        net2ail.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
        echo 'ABC' | ./net2ail.py -t 192.168.1.108 -p 135 # echo text to server port 135
        net2ail.py -t 192.168.1.108 -p 5555 # connect to server
        echo -ne "GET / HTTP/1.1\r\nHost: reachtim.com\r\n\r\n" |python3 ./net2tail.py -t taanilinna.com -p 80 # use the client to send out requests
                                        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nt = Net2ail(args, buffer.encode())
    nt.run()
