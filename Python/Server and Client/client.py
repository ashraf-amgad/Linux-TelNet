#!/usr/bin/env python3

import socket 
import threading 
import sys
import signal, os


if len(sys.argv) != 3:
    print("usage: ./" + sys.argv[0] + " <cli_ip_address> <cli_port>")
    sys.exit(1)


def on_new_client(sck, host_ip, host_port):
	while True:
		try:
			data = sck.recv(1024)
			if len(data) != 0:
				print(data.decode())
			else:
				print("\n[server] terminated ... \nPress enter to terminate the client..")
				sck.close()
				os.exit()
				
		
		except KeyboardInterrupt:
			print("\n[Client] terminated ...")
			sck.close()
			os.exit()
		
		except Exception as e:
			break
		

host_ip = socket.gethostbyname(sys.argv[1])
hname, aliases, hip = socket.gethostbyaddr(host_ip)
print("Trying " + str(hip) + " Connected to " + str(hname) + " Escape character is '^]'.")
host_port = int(sys.argv[2])


sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.connect((host_ip, host_port))
threading._start_new_thread(on_new_client,(sck, host_ip, host_port))


while True:
	try:
		msg = input("")
		sck.sendall(msg.encode('utf-8'))
		if msg =='QUIT':
			print("Connection closed by foreign host.")
			break
		
	except Exception as e:
		break

	except KeyboardInterrupt:
		print("\n[Client] terminated ...")
		sck.close()
		sys.exit()