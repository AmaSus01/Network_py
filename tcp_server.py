import socket
import threading

ip = 'localhost'
port = 9998


def socket_main():
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip,port))
    server.listen(5)  # maximum back-log of  start listen
    print(f'[*] Listening on {ip}:{port}')

    while True:  # connection loop until clients connect
        client, addr = server.accept()
        print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')


if __name__ == '__main__':\
    socket_main()
