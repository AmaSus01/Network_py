import socket

target_host = 'www.google.com'
target_port = 80

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET is is we use our host or ipv4
                                                            # SOCK_STREAM this means we use TCP client
# connect to client
client.connect((target_host, target_port))

# send some data
client.send(b"GET / HTTP/1.1\r\nHosts:google.com\r\n\r\n")  # b - bytes

# get some data
response = client.recv(4096)

print(response.decode())
client.close()