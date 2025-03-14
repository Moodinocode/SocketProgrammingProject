from socket import *
import os

PORT = 8080
ServerIP = "0.0.0.0" # we can also put local host 


def initiateClient(command, filename=None): #command should be sent from the flask web app
  clientSocket = socket(AF_INET,SOCK_STREAM)

  clientSocket.connect((ServerIP,PORT))
  clientSocket.send(str(command).encode()) # send to server the command that we want

  if command == 1:
    print("upload")
    #sending the name of the file
    clientSocket.send(filename.encode())
    
    #sending the contents of the file
    with open(filename, 'rb') as f: # 'r' is for read we use 'rb' since we are dealing with raw data (binary data)
        data = f.read(1024) #defining data as the first KB of the file
        while data:
            clientSocket.send(data) #send each KB at a time
            data = f.read(1024) #redefine data as the next KB
    
  elif command == 2:
    print("download")
    # Send the filename to download
    clientSocket.send(filename.encode())
    
    # Receive the file
    with open(filename, 'wb') as f:
        data = clientSocket.recv(1024)
        while data:
            f.write(data)
            data = clientSocket.recv(1024)
            # Need a way to know when file transfer is complete
            # This is simplified and might need improvement
            
  elif command == 3:
    #listing functionality
    data = clientSocket.recv(4096).decode()
    files_list = data.split(',')
    clientSocket.close()
    return files_list 
    # Return the list to be used by Flask app

  clientSocket.close()


if __name__ == "__main__":
  initiateClient(3)  # Just list files by default