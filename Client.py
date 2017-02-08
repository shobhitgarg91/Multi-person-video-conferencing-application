import cv2
import socket
import pickle
import struct
import sys
from multiprocessing import Process as worker


def sendData(serverPort, serverIP):
    '''
    :param serverPort: The port number of server to send video packets to.
    :param serverIP: The IP address of the server.
    :return:  None

    This method takes in the server ip address and port number as arguments , creates a socket and sends the frame captured
    by web camera through that socket
    '''
    capture = cv2.VideoCapture(0)
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((serverIP, serverPort))
    while True:
        ret, frame = capture.read()
        ret = capture.set(3, 320)
        ret = capture.set(4, 240)
        data = pickle.dumps(frame)
        clientsocket.sendall(struct.pack("i", len(data)) + data)


def recvData(clientPort):
    '''
    :param clientPort:  The port number of the client from which the data is being received
    :return: None

    This method receives the data and stores it in a buffer. Once the entire frame has been received, the frame is loaded back from pickle
    file and displayed in the window using a method from openCV called imshow
    '''
    HOST = ''
    PORT = clientPort
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('Socket created')
    s.bind((HOST, PORT))
    print ('Socket bind complete')
    s.listen(10)
    print ('Socket now listening')

    conn, addr = s.accept()
    print("Connection successful")
    data = ""
    payloadLength = struct.calcsize("i")
    while True:

        while len(data) < payloadLength:
            data += str(conn.recv(4096))
        data = str(data)
        msgSize = data[:payloadLength]
        data = data[payloadLength:]
        msgSize = struct.unpack("i", msgSize)[0]
        while len(data) < msgSize:
            data += str(conn.recv(4096))
        frame_bytes = data[:msgSize]
        data = data[msgSize:]

        frame = pickle.loads(frame_bytes)

        cv2.imshow(str(clientPort), frame)
        cv2.waitKey(1)


def main():
    '''
    Two threads are started for receive data and the send data is called by main thread.
    '''

    print("Enter the number of people to call : ")
    n = int(input(""))
    print ("Enter the ip address of the server")
    ip = sys.stdin.readline()
    ip = ip.strip()
    port = [7001, 9002]
    t = []

    if n == 2:
         t.append(worker(target=recvData ,args = (port[0],)))
         t.append(worker(target=recvData, args= (port[1],)))

         t[0].start()
         t[1].start()
    else:
        t.append(worker(target=recvData, args=(port[0],)))
        t[0].start()

    sendData(6002, ip)



if __name__ == '__main__':
    main()