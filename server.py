#multithreaded TCP file server code
from socket import *
from threading import *
PORT = 8080
files_Array = []
def handle_client(con,addr):
  command = con.recv(1024).decode()
  if command == "1":
    print("upload")
    # Add file upload logic here
  elif command == "2":
    print("download")
    # Add file download logic here
  elif command == "3":
    con.send(",".join(files_Array).encode()) 
  con.close()

def startServer():
  serverSocket = socket(AF_INET,SOCK_STREAM)
  serverSocket.bind(('',PORT))
  serverSocket.listen(10) # 10 clients in queue
  while True:
    connectionSocket, address = serverSocket.accept()
    clientthread = Thread(target = handle_client,args= (connectionSocket,address))
    ##connectionSocket.close(); close in the handle client
    clientthread.start()


if __name__ == "__main__":
  print(f"Server starting on port {PORT}...")
  startServer()