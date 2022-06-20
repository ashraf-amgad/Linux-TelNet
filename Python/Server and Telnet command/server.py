#!/usr/bin/env python3

import socket
import threading 
import sys


if len(sys.argv) != 2:
    print("usage: " + sys.argv[0] + " <svr_port>")
    sys.exit(-1)


ClientPort = int(sys.argv[1])
Clientsck = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )

try:
	Clientsck.bind(('', ClientPort))
	print("Waiting for Incoming Connections...") 
except Exception as e:
	raise SystemExit(f"ERROR:: binding on port: {ClientPort}.")

Clientsck.listen(5)

Number_Of_Registered_Users = [0]
host_data = [0, ""]
DB = [host_data]
host_sockets = []

def get_host_index_with_name(user_name):
	i = 0
	for host in DB:
		if  host[1] == user_name:
			return i
		else:
			i = i + 1
	return -1


def get_host_index_with_fd(fd):
	i = 0
	for host in DB:
		if  host[0] == fd:
			return i
		else:
			i = i + 1
	return -1

def check_user_in_db_with_name(user_name):
	for host in DB:
		if  host[1] == user_name:
			return 1
	return 0


def check_user_in_db_with_fd(fd):
	for host in DB:
		if  host[0] == fd:
			return 1
	return 0


def save_user_in_db(fd, user_name, sock):
	DB.insert(Number_Of_Registered_Users[0], [fd, user_name])
	host_sockets.insert(Number_Of_Registered_Users[0], sock)


def send_LIST(host_sock):
	print_msg = "USER \t\t FD \n-------------------------\n"
	host_sock.sendall(print_msg.encode('utf-8'))
	
	for host in DB:
		if host[0] == 0:
			return
		one_host = host[1] + "\t\t " + str(host[0]) + "\n"
		host_sock.sendall(one_host.encode('utf-8'))

def Send_BCST(BCST):
	for sock in host_sockets:
		sock.sendall(BCST.encode('utf-8'))


def print_DB():
	for host in DB:
		print(host)


def on_new_client(client):
	host_sock = client
	
	host_fd = client.fileno()
	print("Client (" + str(host_fd) + "): Connection Handler Assigned")


	while True:
		try:
			RecvMsg = host_sock.recv(1024)
			SplitMsg = RecvMsg.split()

			# client suddenlly shutdown
			if len(RecvMsg) == 0:
				print(f"Client (" + str(host_fd) + "): QUIT")
				print(f"Client (" + str(host_fd) + "): Disconnecting User.")
				host_index = get_host_index_with_fd(host_fd)
				if host_index != -1:
					DB.pop(host_index)
					host_sockets.pop(host_index)
					Number_Of_Registered_Users[0] = Number_Of_Registered_Users[0] - 1 
					host_sock.close()
				break

			if SplitMsg[0].decode() == 'JOIN':
				if len(SplitMsg) >= 2:
					if Number_Of_Registered_Users[0] < 10:
						check_user_flag = check_user_in_db_with_name(SplitMsg[1].decode())
					
						if check_user_flag == 1:
							print_msg = "User Already Registered. Discarding JOIN."
							print(print_msg)
							print_msg = "User Already Registered: Username (" + SplitMsg[1].decode() + "), FD (" + str(host_fd) + ") \n"
							client.sendall(print_msg.encode('utf-8'))
					
						else:
							print_msg = "JOIN " + SplitMsg[1].decode() + " Request Accepted\n"
							client.sendall(print_msg.encode('utf-8'))
							print_msg = "Client (" + str(host_fd) + "): JOIN " + SplitMsg[1].decode()
							print(print_msg)
							save_user_in_db(host_fd, SplitMsg[1].decode(), host_sock)
							Number_Of_Registered_Users[0] = Number_Of_Registered_Users[0] + 1

					else:
						print("too many users....")
						host_sock.close()
						break

				else:
					print_msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Use \"JOIN <username>\" to Register.\n"
					client.sendall(print_msg.encode('utf-8'))	

			elif SplitMsg[0].decode() == 'LIST':
				check_user_flag = check_user_in_db_with_fd(host_fd)
				if check_user_flag == 1:
					send_LIST(host_sock)
					dash_msg = "-------------------------\n"
					host_sock.sendall(dash_msg.encode('utf-8'))
					print_msg = "Client (" + str(host_fd) + "): LIST"
					print(print_msg)
					
				else:
					print("Unable to Locate Client ("  + str(host_fd) + ") in Database. Discarding LIST.")
					print_msg = "Unregistered User. Use \"JOIN <username>\" to Register.\n"
					host_sock.sendall(print_msg.encode('utf-8'))

			elif SplitMsg[0].decode() == 'MSEG':
				if len(SplitMsg) >= 3:
					check_user_flag = check_user_in_db_with_fd(host_fd)
					if check_user_flag == 1:
						check_user_flag = check_user_in_db_with_name(SplitMsg[1].decode())
						if check_user_flag == 1:
							host_index = get_host_index_with_fd(host_fd)
							MSEG = "FROM " + DB[host_index][1] + ": "
							m = SplitMsg[2:]
							for massage in m:
								MSEG = MSEG + massage.decode() + " "
							MSEG = MSEG + "\n"
							Recipient_index = get_host_index_with_name(SplitMsg[1].decode())
							Recipient_sock = host_sockets[Recipient_index]
							Recipient_sock.sendall(MSEG.encode('utf-8'))
						else:
							print_msg = "Unable to Locate Recipient ("+ SplitMsg[1].decode() + ") in Database. Discarding MESG."
							print(print_msg)
							print_msg = "Unknown Recipient (" + SplitMsg[1].decode() + "). MESG Discarded.\n"
							host_sock.sendall(print_msg.encode('utf-8'))
					else:
						print("Unable to Locate Client ("  + str(host_fd) + ") in Database. Discarding MSEG.")
						print_msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Discarding UNKNOWN Message.\n"
						host_sock.sendall(print_msg.encode('utf-8'))
				else:
					print("client (" + str(host_fd) + ") :Unknown COMMAND. MESG Discarded.")
					print_msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Discarding UNKNOWN Message.\n"
					host_sock.sendall(print_msg.encode('utf-8'))

			elif SplitMsg[0].decode() == 'BCST':
				if len(SplitMsg) >= 2:
					check_user_flag = check_user_in_db_with_fd(host_fd)
					if check_user_flag == 1:
						
							host_index = get_host_index_with_fd(host_fd)
							BCST = "FROM " + DB[host_index][1] + ": "
							m = SplitMsg[1:]
							for massage in m:
								BCST = BCST + massage.decode() + " "
							BCST = BCST + "\n"
							Send_BCST(BCST)
					else:
						print("Unable to Locate Client ("  + str(host_fd) + ") in Database. Discarding BCST.")
						msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Discarding UNKNOWN Message.\n"
						host_sock.sendall(msg.encode('utf-8'))
				
				else:
					print("client (" + str(host_fd) + ") :Unknown COMMAND. MESG Discarded.")
					print_msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Discarding UNKNOWN Message.\n"
					host_sock.sendall(print_msg.encode('utf-8'))

			elif SplitMsg[0].decode() == 'QUIT':
				print(f"Client (" + str(host_fd) + "): QUIT")
				print(f"Client (" + str(host_fd) + "): Disconnecting User.")
				host_index = get_host_index_with_fd(host_fd)
				DB.remove(host_index)
				host_sockets.remove(host_index)
				Number_Of_Registered_Users[0] = Number_Of_Registered_Users[0] - 1 
				host_sock.close()
				break
				
			else:
					print("client (" + str(host_fd) + ") :Unknown COMMAND. MESG Discarded.")
					print_msg = "Client (" + str(host_fd) + "): Unrecognizable Message. Discarding UNKNOWN Message.\n"
					host_sock.sendall(print_msg.encode('utf-8'))

		except Exception as e:
			print(f"Client (" + str(host_fd) + "): QUIT")
			print(f"Client (" + str(host_fd) + "): Disconnecting User.")
			host_index = get_host_index_with_fd(host_fd)
			DB.pop(host_index)
			host_sockets.pop(host_index)
			Number_Of_Registered_Users[0] = Number_Of_Registered_Users[0] - 1 
			host_sock.close()
			break

		


while True:
	try:
		client_connection, ip_port = Clientsck.accept()
		clientfd = client_connection.fileno()
		print("Client (" + str(clientfd) + "): Connection Accepted")
		
		threading._start_new_thread(on_new_client,(client_connection,))


	except KeyboardInterrupt:
		print("")
		Clientsck.close()
		sys.exit()



