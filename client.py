from socket import *

PORT = 8080
ServerIP = "0.0.0.0" # we can also put local host 


def initiateClient(command): #command should be sent from the flask web app
  clientSocket = socket(AF_INET,SOCK_STREAM)

  clientSocket.connect((ServerIP,PORT))
  clientSocket.send(str(command).encode) # send to server the command that we want (if list then we will open a recv for the list of names while if its upload or download then we tell the server to wait for another message from the client either name of file to be downloaded or the file itself)

  if command == 1:
    print("upload")
  elif command == 2:
    print("download")
  elif command == 3:
    #listing functionality
  
    data = clientSocket.recv(4096).decode()
    files_list = data.split(',')
    return files_list 
    # Return the list to be used by Flask app 
    # this might lead to an issue therefore it might be removed

  clientSocket.close()


if __name__ == "__main__":
  initiateClient();