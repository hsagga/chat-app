import socket, select, sys, selectors

if len(sys.argv) != 2: 
    print ("Correct usage: chat, port number")
    exit() 


HEADER_LENGTH = 10
hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
PORT = int(sys.argv[1])
my_username = input("Username: ")
address_list = []
socks = {}
client_1_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_2_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def terminate():
    process_id = int(input("<Connection id>: "))
    for num, address in enumerate(address_list,1):
        if process_id == num:
            print(f'Closing connection...{address}')
            if client_1_server.getpeername() == address:
                client_1_server.close()
            elif client_2_server.getpeername() == address:
                client_2_server.close()
            del address_list[num-1]
        else:
            print("Connection not not found!")


def ip_list():
    print("id: IP address       Port no. ")
    for num, address in enumerate(address_list,1):
        print("{}: {}".format(num,address))

    
def connect():
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    
    dest_ip = input("<destination>: ")
    dest_port = int(input("<port>: "))
    print("connecting to ", dest_ip)

    try:
        client_1_server.send(username_header + username)
        # print("using socket 2")
        client_2_server.connect((dest_ip, dest_port))
        client_2_server.send(username_header + username)
        client_address = client_2_server.getpeername()
        sockets_list = [client_2_server]
    except:
        # print("using socket 1") 
        client_1_server.connect((dest_ip, dest_port))
        client_1_server.send(username_header + username)
        client_address = client_1_server.getpeername()
        sockets_list = [client_1_server]   
    
    print("Connected...")
    address_list.append(client_address)
    


        
    
def myport():
    print('Active on port:', PORT)


def myip():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print("IP Address: ", ip_address)


def receive_message(client_socket):
    try:
        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False
        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())
        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except:
        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    sockets_list = [server_socket]
    clients = {}
    print(f'Listening for connections on {IP}:{PORT}...') 

    while True:
        read_sockets, _, exception_sockets = select.select(
            sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                # Accept new connection
                # That gives us new socket - client socket, connected to this given client only, it's unique for that client
                # The other returned object is ip/port set
                client_socket, client_address = server_socket.accept()
                # Client should send his name right away, receive it
                user = receive_message(client_socket)
                # If False - client disconnected before he sent his name
                if user is False:
                    continue
                # Add accepted socket to select.select() list
                sockets_list.append(client_socket)
                # Also save username and username header
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(
                    *client_address, user['data'].decode('utf-8')))   
                address_list.append(client_address)
                break
            # Else existing socket is sending a message
            else:
                #break
                
                message = receive_message(notified_socket)
                # If False, client disconnected, cleanup
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                    # Remove from list for socket.socket()
                    sockets_list.remove(notified_socket)
                    # Remove from our list of users
                    del clients[notified_socket]
                    continue
                # Get user by notified socket, so we will know who sent the message
                user = clients[notified_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
        # It's not really necessary to have this, but will handle some socket exceptions just in case
        for notified_socket in exception_sockets:
            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)
            # Remove from our list of users
            del clients[notified_socket]
        # menu()


def client():
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')


def send():
    con_id = int(input("<Connection id>: "))
    while True:
        # Wait for user to input a message
        message = input(f'{my_username} > ')
        # If message is not empty - send it
        if message:
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            
            addr = client_1_server.getpeername()
            addr2 = client_2_server.getpeername()
            for num, address in enumerate(address_list,1):
                if con_id == num:
                    print("connection avaliable")
                    if addr == address:
                        print("socket 1")
                        client_1_server.send(message_header + message)
                    if addr2 == address:
                        print("socket 2")
                        client_2_server.send(message_header + message)
            addr = client_1_server.getpeername()
            print(f'Message sent to: "{addr}')
            break
            

def menu():
    print("1> help\n2> myip\n3> myport\n4> connect") 
    print("5> list\n6> terminate\n7> send\n8> exit")
    option = input()
    if option == '1':
        menu()
    if option == '2':
        myip()
        menu()
    if option == '3':
        myport()
        menu()
    if option == '4':
        connect()
        menu()
    if option == '5':
        ip_list()
        menu()
    if option == '6':
        terminate()
        menu()
    if option == '7':
        send()
        menu()
    if option == '8':
        exit()


print("1. server\n2. client")
option = input()
if option == "1":
    server()
    menu()
if option == "2":
    client()
    menu()