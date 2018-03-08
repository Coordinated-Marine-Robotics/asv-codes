import socket

UDP_IP = '192.168.0.57'	#RPI's IP Address
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Internet and UDP
sock.bind(MESSAGE, (UDP_IP, UDP_PORT))

while True:
	data, addr = sock.recvfrom(1024) #buffer size is 1024 bytes (4096 for 4k)
	print "receive message:", data