#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

int Number_Of_Registered_clients;
char buffer[100];

typedef struct
{
	int cli_fd;
	char cli_name[25];

} client_typedef;
client_typedef clients[10];

void *thread_handler(void *fd);

int main(int argc, char *argv[])
{
	struct sockaddr_in server;
	pthread_t th_num;

	int fd1, fd2, server_size;
	int *newsock;

	if (argc != 2)
	{
		printf("Error: usage ./%s <port> ..\n", argv[0]);
		exit(0);
	}

	if ((fd1 = socket(AF_INET, SOCK_STREAM, 0)) == -1)
	{
		printf("Error: open socket.\n");
		exit(0);
	}

	server.sin_family = AF_INET;
	server.sin_addr.s_addr = htonl(INADDR_ANY);
	server.sin_port = htons(atoi(argv[1]));

	if (bind(fd1, (struct sockaddr *)&server, sizeof(server)) < 0)
	{

		printf("Error: bind to socket..\n");
		exit(0);
	}

	if (listen(fd1, 10) < 0)
	{
		printf("Error listen to socket..\n");
		exit(0);
	}

	printf("Waiting for Incoming Connections...\n");

	server_size = sizeof(server);
	while (fd2 = accept(fd1, (struct sockaddr *)&server, &server_size))
	{
		printf("Client (%d): Connection Accepted\n", fd2);

		int *thread_fd = (int *)malloc(sizeof(int));
		thread_fd = &fd2;

		if (pthread_create(&th_num, NULL, thread_handler, (void *)thread_fd) < 0)
		{
			perror("Error Creating thread.\n");
			exit(0);
		}
		else
		{
			printf("Client (%d): Connection Handler Assigned\n", *thread_fd);
		}
	}
}

void split_massage(char *massage, char *split_massage[10])
{
	int i, j;
	i = 0;
	split_massage[i] = strtok(massage, " ");

	while (split_massage[i] != NULL)
	{
		i++;
		split_massage[i] = strtok(NULL, " ");
	}
}

int check_cli_in_db_with_fd(int fd)
{
	int i = 0;

	while (i < 10)
	{
		if (clients[i].cli_fd == fd)
			return 1;

		else
			i++;
	}

	return 0;
}

int check_cli_in_db_with_name(char *user_name)
{
	int i = 0;

	while (i < 10)
	{
		if (strcmp(clients[i].cli_name, user_name) == 0)
			return 1;

		else
			i++;
	}

	return 0;
}

int get_cli_index_with_name(char *user_name)
{
	int i = 0;

	while (i < 10)
	{
		if (strcmp(clients[i].cli_name, user_name) == 0)
			return i;

		else
			i++;
	}

	return -1;
}

int get_cli_index_with_fd(int fd)
{
	int i = 0;

	while (i < 10)
	{
		if (clients[i].cli_fd == fd)
			return i;

		else
			i++;
	}

	return -1;
}

void save_cli_in_db(int fd, char *user_name)
{
	clients[Number_Of_Registered_clients].cli_fd = fd;
	strcpy(clients[Number_Of_Registered_clients].cli_name, user_name);
}

void Send_List_Of_Registered_Users(int fd)
{
	int i = 0;

	memset(buffer, '\0', sizeof(buffer));
	sprintf(buffer, "------------------------\nUSER NAME\tFD\n------------------------\n");
	write(fd, buffer, strlen(buffer));

	i = 0;
	while (i < Number_Of_Registered_clients)
	{
		memset(buffer, '\0', sizeof(buffer));
		sprintf(buffer, "%s\t\t%d\n", clients[i].cli_name, clients[i].cli_fd);
		write(fd, buffer, strlen(buffer));
		i++;
	}

	memset(buffer, '\0', sizeof(buffer));
	sprintf(buffer, "------------------------\n");
	write(fd, buffer, strlen(buffer));
}

void remove_client_from_db(int user_index)
{
	int i = user_index;

	while (i < 10)
	{
		strcpy(clients[i].cli_name, clients[i + 1].cli_name);
		clients[i].cli_fd = clients[i + 1].cli_fd;
		i++;
	}
}

void *thread_handler(void *thread_fd)
{
	char rcv_msg[200];
	char *split_msg[10];

	int cli_fd = *(int *)thread_fd;
	int n;
	while ((n = recv(cli_fd, rcv_msg, 200, 0)) > 0)
	{
		rcv_msg[n - 2] = '\0';
		split_massage(rcv_msg, split_msg);


		if (strcmp(split_msg[0], "JOIN") == 0)
		{
			if (split_msg[1] == NULL)
			{
				printf("Client (%d): Unrecognizable Message. Discarding UNKNOWN Message\n", cli_fd);
				sprintf(buffer, "Client (%d): Unrecognizable Message. Use \"JOIN <username>\" to Register.\n", cli_fd);
				write(cli_fd, buffer, strlen(buffer));
			}

			else
			{

				int found_user_flag = check_cli_in_db_with_name(split_msg[1]);

				if (found_user_flag == 1)
				{
					printf("Client (%d): User Already Registered. Discarding JOIN.\n", cli_fd);
					memset(buffer, '\0', sizeof(buffer));
					int client_index = get_cli_index_with_name(split_msg[1]);
					sprintf(buffer, "User Already Registered: Username (%s), FD (%d)\n", split_msg[1], clients[client_index].cli_fd);
					write(cli_fd, buffer, strlen(buffer));
				}

				else
				{
					if (Number_Of_Registered_clients < 10)
					{
						clients[Number_Of_Registered_clients].cli_fd = cli_fd;
						strcpy(clients[Number_Of_Registered_clients].cli_name, split_msg[1]);
						Number_Of_Registered_clients++;
						printf("Client (%d): JOIN %s\n", cli_fd, split_msg[1]);
						memset(buffer, '\0', sizeof(buffer));
						sprintf(buffer, "JOIN %s Request Accepted\n", split_msg[1]);
						write(cli_fd, buffer, strlen(buffer));
					}

					else
					{
						printf("...\n\
								Client (25): Database Full. Disconnecting User.\n\
								...\n\
								Error: Too Many Clients Connected\n\
								...\n");

						memset(buffer, '\0', sizeof(buffer));
						sprintf(buffer, "Too Many Users. Disconnecting User.\nConnection closed by foreign host.\n...\n");
						write(cli_fd, buffer, strlen(buffer));
						close(cli_fd);
						break;
					}
				}
			}
		}

		else if (strcmp(split_msg[0], "LIST") == 0)
		{
			int check_regiestered_user_flag = check_cli_in_db_with_fd(cli_fd);
			if (check_regiestered_user_flag == 1)
			{
				printf("Client (%d) : LIST\n", cli_fd);
				Send_List_Of_Registered_Users(cli_fd);
			}
			else
			{
				printf("Unable to Locate Client (%d) in Database. Discarding LIST.\n", cli_fd);
				memset(buffer, '\0', sizeof(buffer));
				sprintf(buffer, "Unregistered User. Use \"JOIN <username>\" to Register.\n");
				write(cli_fd, buffer, strlen(buffer));
			}
		}

		else if (strcmp(split_msg[0], "MSEG") == 0)
		{
			if ((split_msg[1] != NULL) && (split_msg[2] != NULL))
			{
				int check_regiestered_user_flag = check_cli_in_db_with_fd(cli_fd);
				if (check_regiestered_user_flag == 1)
				{
					int check_Recipient_flag = check_cli_in_db_with_name(split_msg[1]);
					if (check_Recipient_flag == 1)
					{
						int Recipient_index = get_cli_index_with_name(split_msg[1]);
						int cli_index = get_cli_index_with_fd(cli_fd);
						memset(buffer, '\0', strlen(buffer));
						sprintf(buffer, "FROM %s: ", clients[cli_index].cli_name);
						write(clients[Recipient_index].cli_fd, buffer, strlen(buffer));

						int i = 0;
						while (split_msg[i + 2] != NULL)
						{
							memset(buffer, '\0', strlen(buffer));
							sprintf(buffer, "%s ", split_msg[i + 2]);
							write(clients[Recipient_index].cli_fd, buffer, strlen(buffer));
							i++;
						}

						memset(buffer, '\0', strlen(buffer));
						sprintf(buffer, " \n");
						write(clients[Recipient_index].cli_fd, buffer, strlen(buffer));
					}

					else
					{
						printf("Unable to Locate Recipient (%s) in Database. Discarding MSEG.\n", split_msg[1]);
						memset(buffer, '\0', strlen(buffer));
						sprintf(buffer, "Unable to Locate Recipient (%s) in Database. Discarding MSEG.\n", split_msg[1]);
						write(cli_fd, buffer, strlen(buffer));
					}
				}

				else
				{
					printf("Unable to Locate Client (%d) in Database. Discarding MSEG.\n", cli_fd);
					memset(buffer, '\0', strlen(buffer));
					sprintf(buffer, "Client (%d): Unrecognizable Message. Discarding UNKNOWN Message.\n", cli_fd);
					write(cli_fd, buffer, strlen(buffer));
				}
			}

			else
			{
				printf("Client (%d): Unknown COMMAND. MESG Discarded.\n", cli_fd);
				memset(buffer, '\0', strlen(buffer));
				sprintf(buffer, "Unrecognizable Message. Discarding UNKNOWN Message.\n");
				write(cli_fd, buffer, strlen(buffer));
			}
		}

		else if (strcmp(split_msg[0], "BCST") == 0)
		{
			if (split_msg[1] != NULL)
			{
				int check_regiestered_user_flag = check_cli_in_db_with_fd(cli_fd);
				if (check_regiestered_user_flag == 1)
				{
					int BCST_from_user_index = get_cli_index_with_fd(cli_fd);

					int i = 0;
					int j = 0;
					while (i < Number_Of_Registered_clients)
					{
						memset(buffer, '\0', strlen(buffer));
						sprintf(buffer, "FROM %s: ", clients[BCST_from_user_index].cli_name);
						write(clients[i].cli_fd, buffer, strlen(buffer));

						j = 0;
						while (split_msg[j + 1] != NULL)
						{
							memset(buffer, '\0', strlen(buffer));
							sprintf(buffer, "%s ", split_msg[j + 1]);
							write(clients[i].cli_fd, buffer, strlen(buffer));
							j++;
						}

						memset(buffer, '\0', strlen(buffer));
						sprintf(buffer, " \n");
						write(clients[i].cli_fd, buffer, strlen(buffer));
						i++;
					}
				}

				else
				{
					printf("Unable to Locate Client (%d) in Database. Discarding BCST.\n", cli_fd);
					memset(buffer, '\0', strlen(buffer));
					sprintf(buffer, "Client (%d): Unrecognizable Message. Discarding UNKNOWN Message.\n", cli_fd);
					write(cli_fd, buffer, strlen(buffer));
				}
			}

			else
			{
				printf("Client (%d): Unrecognizable Message. Discarding UNKNOWN Message.\n", cli_fd);
				memset(buffer, '\0', strlen(buffer));
				sprintf(buffer, "Unrecognizable Message. Discarding UNKNOWN Message.\n");
				write(cli_fd, buffer, strlen(buffer));
			}
		}

		else if (strcmp(split_msg[0], "QUIT") == 0)
		{
			int check_regiestered_user_flag = check_cli_in_db_with_fd(cli_fd);

			if (check_regiestered_user_flag == 1)
			{

				int UserIndex = get_cli_index_with_fd(cli_fd);
				remove_client_from_db(UserIndex);
				Number_Of_Registered_clients--;
				printf("Client (%d): QUIT\nClient (%d): Disconnecting User.\n", cli_fd, cli_fd);
				close(cli_fd);
				break;
			}

			else
			{
				printf("Client (%d): QUIT\nClient (%d): Disconnecting User.\n", cli_fd, cli_fd);
				close(cli_fd);
				break;
			}
		}

		else
		{
			printf("Client (%d): Unrecognizable Message. Discarding UNKNOWN Message.\n", cli_fd);
			memset(buffer, '\0', strlen(buffer));
			sprintf(buffer, "Unknown Message. Discarding UNKNOWN Message.\n");
			write(cli_fd, buffer, strlen(buffer));
		}
	}
}
