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
    # Receive the file
    with open(filename, 'wb') as f:
        data = clientSocket.recv(1024)
        while data:
            f.write(data)
            data = clientSocket.recv(1024)
            # Need a way to know when file transfer is complete
            # This is simplified and might need improvement
            #copied from the download of client 
            # must add connection to database
  elif command == "2":
    print("download")
    # Add file download logic here
    #sending the contents of the file
    with open(filename, 'rb') as f: # 'r' is for read we use 'rb' since we are dealing with raw data (binary data)
        data = f.read(1024) #defining data as the first KB of the file
        while data:
            clientSocket.send(data) #send each KB at a time
            data = f.read(1024) #redefine data as the next KB
            #coppied directly from client upload hence might need fixing
    
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