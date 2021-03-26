import socket

target_host = '127.0.0.1'
target_port = 9997  # TCP/UDP port

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b"Pupa and Lupa", (target_host, target_port))

# get some data
data, addr = client.recvfrom(4096)  # 4096 TCP/UDP port

print(data.decode())
client.close()
