
from threading import Thread as worker
from multiprocessing import Process as worker
import multiprocessing

import socket
import sys
import struct
import threading
counterReady = 0
threadLock = threading.Lock()

def CreateReceiveSockets(Receive_Video_From):
    '''
    This method ctakes in a dictionary of each user and creates the sockets for receiving the video frames from each client
    :param Receive_Video_From: dictionary of ports to create sockets
    :return:  None
    '''
    Receive_Sockets_map = {}

    for key in Receive_Video_From.keys():
        Receive_Sockets_map[key] = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        Receive_Sockets_map[key].bind(('',Receive_Video_From[key]))
    return Receive_Sockets_map



def listenToClients(numUsers,counterReady,socket, SendingInformation,threadNumber ):
    '''
    :param numUsers:  The number of users
    :param counterReady:  The counter to check if all the users are ready to listen
    :param socket:  the dictionary of sockets to send to
    :param SendingInformation: the data to be sent
    :param threadNumber: the thread number which has teh lock over this function
    :return: None
    '''

    print "\nlistening to client numUsers =",numUsers.value," user id =",threadNumber


    socket.listen(10)

    conn,addr = socket.accept()


    counterReady.value += 1

    data = ""
    payloadLength = struct.calcsize("i")


    flag = False

    print(counterReady.value)
    while True:
        print(counterReady.value)
        print("Thread "+str(threadNumber) + " Receiving")
        while len(data) < payloadLength:
            data += str(conn.recv(4096))
        data = str(data)
        msgSize = data[:payloadLength]
        data = data[payloadLength:]
        # msgSize = str.encode(msgSize)
        msg_size = struct.unpack("i", msgSize)[0]
        while len(data) < msg_size:
            data += str(conn.recv(4096))
        frame_data = data[:msg_size]
        data = data[msg_size:]



        if counterReady.value == numUsers.value:
             if flag ==False:
                print ("counter is "+ str(numUsers.value))
                for key in SendingInformation.keys():
                    t = SendingInformation[key]
                    print("t[0]: ",str(t[0]))
                    print("t[1]: ",str(t[1]))
                    print("t[2]: ",str(t[2]))
                    t[0].connect((t[2],int(t[1])))

                flag=True

             for key in SendingInformation.keys():

                print ("sending frames to " + str(SendingInformation[key]))
                SendingInformation[key][0].sendall(struct.pack("i", len(frame_data))+frame_data)



def CreateSendingSockets(Server_Ports_To_Send_From, IPAddressTable,clientPortsToSend):
    '''
    :param Server_Ports_To_Send_From: The ports of the server to send form
    :param IPAddressTable: The ip addresses to send to
    :param clientPortsToSend: The port number of client to send to
    :return: None
    '''
    Sending_Sockets_map = {}

    for key1 in Server_Ports_To_Send_From.keys():
        Sending_Sockets_map[key1] = {}
        for key2 in Server_Ports_To_Send_From[key1].keys():
            Sending_Sockets_map[key1][key2]= [socket.socket(socket.AF_INET,socket.SOCK_STREAM),
                                              clientPortsToSend[key1][key2],IPAddressTable[key2] ]

    return Sending_Sockets_map

def main():

    numberOfUsers = int(input("Enter the number of users : "))
    ClientipAddresses = {}

    for i in range(0,numberOfUsers):
        print "\nEnter IP address of user "+str((i+1))+ " :",
        line = sys.stdin.readline()
        line = line.strip()
        ClientipAddresses[i+1] = line

    Server_Ports_To_Send_From = {}
    Clients_Ports_To_Send = {}

    Receive_Video_From = {}

    if(numberOfUsers == 3):
        Server_Ports_To_Send_From[1] = {2: 6004, 3: 6005}
        Server_Ports_To_Send_From[2] = {1: 6006, 3: 6007}
        Server_Ports_To_Send_From[3] = {2: 6009, 1: 6008}

        Clients_Ports_To_Send[1] = {2: 7001, 3: 7002}
        Clients_Ports_To_Send[2] = {1: 8001, 3: 8002}
        Clients_Ports_To_Send[3] = {2: 9002, 1: 9001}

        Receive_Video_From[1] = 6001
        Receive_Video_From[2] = 6002
        Receive_Video_From[3] = 6003
    else:
        Server_Ports_To_Send_From[1] = {2: 6004}
        Server_Ports_To_Send_From[2] = {1: 6006}

        Clients_Ports_To_Send[1] = {2: 7001}
        Clients_Ports_To_Send[2] = {1: 8001}

        Receive_Video_From[1] = 6001
        Receive_Video_From[2] = 6002

    manager = multiprocessing.Manager()


    counterReady = manager.Value('i',0)
    numUsers = manager.Value('i',numberOfUsers)


    Receive_Sockets_map = CreateReceiveSockets(Receive_Video_From)
    Sending_Sockets_map = CreateSendingSockets(Server_Ports_To_Send_From,ClientipAddresses,Clients_Ports_To_Send)

    keySet = Receive_Sockets_map.keys()

    t = []
    for i in range(0,numberOfUsers):

         if i == numberOfUsers-1 :
             listenToClients(numUsers,counterReady,Receive_Sockets_map[keySet[i]] , Sending_Sockets_map[keySet[i]], i)
         t.append(worker(target=listenToClients, args=(numUsers,counterReady,Receive_Sockets_map[keySet[i]] , Sending_Sockets_map[keySet[i]],i)))
         t[i].start()


if __name__ == "__main__":
    main()