#multithreaded TCP file server code
from socket import *
from threading import *
PORT = 8080

def handle_client(con,addr):


  con.close()

def startServer():
  serverSocket = socket(socket.AF_INET,socket.SOCK_STREAM)
  serverSocket.bind(('',PORT))
  serverSocket.listen(10) # 10 clients in queue
  while True:
    connectionSocket, address = serverSocket.accept()
    clientthread = threading.Thread(target = handle_client,args= (connectionSocket,address))
    ##connectionSocket.close(); close in the handle client
    clientthread.start()