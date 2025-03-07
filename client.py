from socket import *

PORT = 8080
ServerIP = "0.0.0.0" # we can also put local host 


def initiateClient():
  clientSocket = socket(AF_INET,SOCK_STREAM)
  clientSocket.connect((ServerIP,PORT))
  #client functionality
  clientSocket.close()


if __name__ == "__main__":
  initiateClient();