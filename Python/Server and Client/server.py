#!/usr/bin/env python3

import socket
import threading 
import sys
import signal, os


if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " <svr_port>")
    sys.exit(1)


host_port = int(sys.argv[1])

sck = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
	sck.bind(('', host_port))
	sck.listen(10)
	print("Waiting for Incoming Connections...") 
except Exception as e:
	raise SystemExit(f"We could not bind the server on host: {host_ip} to port: {host_port}, because: {e}")



Max_UserNumber = 10
UserNumber = [0]
UsersNamedb  = [" " , " " , " " , " " , " " ," " , " " , " " , " " , " "]
UsersFDdb = [-1 , -1 , -1 , -1 , -1 , -1 , -1 , -1 , -1 , -1]
UsersPort = [-1 , -1 , -1 , -1 , -1 , -1 , -1 , -1 , -1 , -1]
UsersConnection = []


def on_new_client(client, connection):
	ip = connection[0]
	port = connection[1]
	flag = 0

	fd = client.fileno()
	
	print("Client (" + str(fd) + "): Connection Handler Assigned")

	#print(f"THe new connection was made from IP: {ip}, and port: {port}!")
	while True:
		try:
			msg = client.recv(1024)
			splitted_msg = msg.split()

			index = 0
			for userport in UsersPort:
				if userport != port:
					index = index + 1
				else:
					break


			if UserNumber[0] < Max_UserNumber:
				if splitted_msg[0].decode() == 'JOIN':
					if index < 10:
						# user name is exsiting
						d0 = "User Already Registered. Discarding JOIN."
						print(d0)
						d0 = "User Already Registered: Username (" + splitted_msg[1].decode() + ") , FD (" + str(fd) + ")"
						client.sendall(d0.encode('utf-8'))
						flag = 0
					else:
						if len(splitted_msg) < 2:
							cxz = "Client (" + str(fd) + "): Unrecognizable Message. Use \"JOIN <username>\" to Register."
							client.sendall(cxz.encode('utf-8'))	
						else:
							# user name is not exsiting
							dxc = "JOIN " + splitted_msg[1].decode() + " Request Accepted"
							client.sendall(dxc.encode('utf-8'))
							dxc = "Client (" + str(fd) + "): JOIN " + splitted_msg[1].decode()
							print(dxc)
							UsersNamedb.insert(UserNumber[0], splitted_msg[1].decode())
							UsersFDdb.insert(UserNumber[0], fd)
							UsersPort.insert(UserNumber[0], port)
							UsersConnection.insert(UserNumber[0], client)
							UserNumber[0] = UserNumber[0] + 1

				elif splitted_msg[0].decode() == 'LIST':
					if index < 10:
						# check if user name already exist
						# if user is already exist then LIST registered clients
						# if not send massage to joins
						da = "-------------------------\nUSER \t FD \n"
						client.sendall(da.encode('utf-8'))
						ind = 0
						for name in UsersNamedb:
							if name != ' ':
								ind = ind + 1
						indx = 0
						while indx < ind:
							LIST =  UsersNamedb[indx] + "\t  " + str(UsersFDdb[indx]) + "\n"
							#for cli in UsersConnection:
							client.sendall(LIST.encode('utf-8'))
							indx = indx + 1 
						da = "-------------------------\n"
						client.sendall(da.encode('utf-8'))
						dxc = "Client (" + str(UsersFDdb[index]) + "): LIST"
						print(dxc)
						flag = 0
					
					else:
						print("Unable to Locate Client ("  + str(fd) + ") in Database. Discarding LIST.")
						cxz = "Unregistered User. Use \"JOIN <username>\" to Register."
						client.sendall(cxz.encode('utf-8'))

				elif (splitted_msg[0].decode() == 'MSG') or (splitted_msg[0].decode() == 'BCST'):
					if index < 10:
						username = UsersNamedb[index]
						massage_MSG = "FROM " + username + " : "

						if splitted_msg[0].decode() == 'MSG':
							massg = splitted_msg[2:]
							for massage in massg:
								massage_MSG = massage_MSG + massage.decode() + " "

							if len(splitted_msg) < 3:
								print("Unable to Locate Client ("  + str(fd) + ") in Database. Discarding MSG.")
								cxz = "Client (" + str(UsersFDdb[index]) + "): Unrecognizable Message. Discarding UNKNOWN Message."
								client.sendall(cxz.encode('utf-8'))	
							else:
								flg = 0
								for na in UsersNamedb:
									if na ==  splitted_msg[1].decode():
										flg = 1
										break
									else:
										flg = 0
								if flg == 1:
									ind = 0
									for usertosend in UsersNamedb:
										if usertosend != splitted_msg[1].decode():
											ind = ind + 1
										else:
											break
									clienttosend = UsersConnection[ind]
									clienttosend.sendall(massage_MSG.encode('utf-8'))
								else:
									cxz0 = "Unable to Locate Recipient ("+ splitted_msg[1].decode() + ") in Database. Discarding MESG."
									print(cxz0)
									cxz0 = "Unknown Recipient (" + splitted_msg[1].decode() + "). MESG Discarded."
									UsersConnection[index].sendall(cxz0.encode('utf-8'))		
						else:
							massg = splitted_msg[1:]
							for massage in massg:
								massage_MSG = massage_MSG + massage.decode() + " "

							if len(splitted_msg) < 2:
								print("Unable to Locate Client ("  + str(fd) + ") in Database. Discarding BCST.")
								cxz = "Client (" + str(UsersFDdb[index]) + "): Unrecognizable Message. Discarding UNKNOWN Message."
								client.sendall(cxz.encode('utf-8'))
							else:
								for clienttosend in UsersConnection:
									if clienttosend != UsersConnection[index]:
										clienttosend.sendall(massage_MSG.encode('utf-8'))
						
						flag = 0
					else:
						if splitted_msg[0].decode() == 'MSG':
							print("Unable to Locate Client ("  + str(fd) + ") in Database. Discarding MESG.")
						if splitted_msg[0].decode() == 'BCST':
							print("Unable to Locate Client ("  + str(fd) + ") in Database. Discarding BCST.")	
						cxz = "Unregistered User. Use \"JOIN <username>\" to Register."
						client.sendall(cxz.encode('utf-8'))		
			
				elif msg.decode() == 'QUIT':
					if index < 10:
						#remove the client from data base 
						#and decrease number of registered client with one
						dsa = "Connection closed by foreign host."
						UsersConnection[index].sendall(dsa.encode('utf-8'))
						cxzz = "Client (" + str(UsersFDdb[index]) + "): QUIT"
						print(cxzz)
						UsersNamedb.remove(UsersNamedb[index])
						UsersPort.remove(UsersPort[index])
						UsersFDdb.remove(UsersFDdb[index])
						UsersConnection.remove(UsersConnection[index])
						UserNumber[0] = UserNumber[0] - 1 
						break
					
					else:
						cxzz = "Client (" + str(fd) + "): QUIT\n" + "Client (" + str(fd) + "): Disconnecting User."  
						print(cxzz)
						break
				
				else:
					print("client (" + str(fd) + ") :Unknown COMMAND. MESG Discarded.")
			else:
				print("... Client ("+ str(fd) +"): Database Full. Disconnecting User....\nError: Too Many Clients Connected...")
				mscx = "Too Many Users. Disconnecting User. Connection closed by foreign host...."
				client.sendall(mscx.encode('utf-8'))				
				client.close()
				break
				
		
		except Exception as e:
			raise SystemExit(f"Client (" + str(fd) + "): QUITED")
			break

while True:
	try:
		client, ip = sck.accept()
		fd = client.fileno()
		print("Client (" + str(fd) + "): Connection Accepted")
		t = threading._start_new_thread(on_new_client,(client, ip))


	except KeyboardInterrupt:
		print("\n[server] terminated ...")
		sck.close()
		sys.exit()



