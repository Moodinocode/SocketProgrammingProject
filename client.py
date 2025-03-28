from socket import *
import os

PORT = 8080
ServerIP = "0.0.0.0" # we can also put local host 


def initiateClient(command, filename=None): #command should be sent from the flask web app
  try:
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
      filesize = clientSocket.recv(1024)
      current = 0
      
      # Receive the file
      with open(filename, 'wb') as f:
          while True:
              data = clientSocket.recv(1024)
              if not data or data == b"FILE_NOT_FOUND":
                  break
              f.write(data)
              if len(data) < 1024:  # Last packet might be smaller
                  break
              current += len(data)  # Corrected to use len(data)
              progress = (current / int(filesize)) * 100  # Calculate progress
              log("info", f"Downloading: {progress:.2f}%")
                
    elif command == 3:
      #listing functionality
      data = clientSocket.recv(4096).decode()
      files_list = data.split(',')
      return files_list 
      # Return the list to be used by Flask app

  except Exception as e:
    log("error", f"Error in client operation: {str(e)}")
  finally:
    clientSocket.close()


if __name__ == "__main__":
  initiateClient(3)  # Just list files by default