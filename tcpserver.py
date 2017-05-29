#!/usr/bin/python

import socket
import threading

#TCP Server 

bind_ip	= "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

server.listen(5)

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

#Client handeling thread

def handle_client(client_socket):

	#print what the client sends
	request = client_socket.recv(1024)

	print "[*] Received: %s" % request

	#send back packet
	client_socket.send("Shit!")

	client_socket.close()

while True:

	client,addr = server.accept()

	print "[*] Accepted connection from: %s:%d" % (addr[0], addr[1])

	#spin up client thread to handle incoming data

	client_handler = threading.Thread(target=handle_client,args=(client,))
	client_handler.start()
