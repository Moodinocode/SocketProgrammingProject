from socket import *

PORT = 8080
ServerIP = "0.0.0.0" # we can also put local host 


def initiateClient(command): #command should be sent from the flask web app
  clientSocket = socket(AF_INET,SOCK_STREAM)
  clientSocket.connect((ServerIP,PORT))
  #client functionality
  # Step 1 take from client 3 parameters
  # (command, file name,file) 
  # Command are file operations uplaod/downlaod/list
  # filename should be either the name of the file that is being uploaded or the one being requrested to be dowloaded
  # file should be the file being uploaded
  if command == 1:
    print("upload")
  elif command == 2:
    print("download")
  elif command == 3:
    print("list")

  clientSocket.close()


if __name__ == "__main__":
  initiateClient();