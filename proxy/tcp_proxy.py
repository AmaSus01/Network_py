import sys
import socket
import threading


hex_filter = ''.join([(len(repr(chr(i)))==3) and chr(i) or '.' for i in range(256)])  # that contains ASCII printable characters


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):  # нас есть строка, декодирующая байты, если байтовая строка была передана
        src = src.decode()
    result = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])  # берем кусок строки для сброса и помещаем его в переменную word

        # используем встроенную функцию translate для замены строкового представления каждого символа на соответствующий символ в необработанной строке (для печати)
        printable = word.translate(hex_filter)
        hex = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        result.append(f'{i:04x} {hex:<{hexwidth}} {printable}')
    if show:
        for line in result:
            print(line)
        else:
            return result


def receive_from(connection):
    # создаем пустую байтовую строку, buffer, в которой будут накапливаться ответы от сокета.
    buffer = b''
    connection.settimeout(20)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data

    except Exception as e:
        pass
    return buffer


def requests_h(buffer):
    # packet modification
    return buffer


def response_h(buffer):
    # packet modification
    return buffer


def proxy_h(client_socket, remote_host, remote_port, receive): # подключение к удаленному хосту
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive:  # запрашиваем дату перед тем как уйти в основной цикл
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_h(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(remote_socket)


        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = requests_h(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")


        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_h(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(localhost, local_port, remote_host, remote_port, receive):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket

    try:
        server.bind((localhost, local_port)) # bind to the localhost and listen
    except Exception as e:
        print('problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (localhost, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (localhost, local_port))
    server.listen(5)

    while True:
        client_socket, addr  = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)

# когда поступает новый запрос на соединение, мы передаем его proxy_h в новом потоке, который выполняет всю отправку и получение битов
        proxy_thread = threading.Thread(  # start a thread to talk to the remote host
            target = proxy_h,
            args = (client_socket, remote_host, remote_port, receive))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./tcp_proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive]")
        print("Example: ./tcp_proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    localhost = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive = sys.argv[5]

    if "True" in receive:
        receive = True
    else:
        receive = False

    server_loop(localhost, local_port, remote_host, remote_port, receive)


if __name__ == '__main__':
    main()