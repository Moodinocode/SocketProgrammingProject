from socket import *
import os
import requests
import time
from utils import log
import hashlib

PORT = 8080
ServerIP = "127.0.0.1"  # Use localhost

def initiateClient(command, file_path=None, original_filename=None): #command should be sent from the flask web app
  try:
    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((ServerIP,PORT))
    clientSocket.send(str(command).encode()) # send to server the command that we want
    time.sleep(1)

    if command == 1:
      if not file_path:
        log("error", "No file path provided for upload")
        return
        
      log("info", f"Uploading file: {file_path}")
      # Extract just the filename from the path
      filename = os.path.basename(file_path)
      
      #sending the name of the file
      clientSocket.send(filename.encode())
      hash_object = hashlib.sha256()
      
      #sending the contents of the file
      with open(file_path, 'rb') as f:
          total_size = os.path.getsize(file_path)
          sent = 0
          data = f.read(4096)
          while data:
              hash_object.update(data)
              clientSocket.send(data)
              sent += len(data)
              progress = (sent / total_size) * 100
              # Send progress to the Flask app
              requests.post('http://localhost:5000/update_progress', 
                           json={"filename": filename, "progress": progress})
              data = f.read(4096)
              if total_size < 5 * 1024 * 1024:  
                  time.sleep(0.1) #delay for small files (<5MB) in order to be able to see the progress bar 
      # Send final 100% progress update
      requests.post('http://localhost:5000/update_progress', 
                   json={"filename": filename, "progress": 100})
      # Send the hash to verify file integrity
      clientSocket.send(hash_object.hexdigest().encode())
      # Wait for server's verification response
      verification = clientSocket.recv(1024).decode()
      if verification != "OK":
          log("error", "File integrity check failed during upload")
          return
    
    elif command == 2:
      if not file_path:
        log("error", "No file path provided for download")
        return
        
      log("info", f"Downloading file: {file_path}")
      
      # Use the original filename if provided, otherwise extract from path
      if original_filename:
          filename = original_filename
      else:
          # Extract just the filename from the path
          filename = os.path.basename(file_path)
      
      # Send the filename to download
      clientSocket.send(filename.encode())
      filesize = clientSocket.recv(1024).decode()
      hash_object = hashlib.sha256()

      if filesize == "FILE_NOT_FOUND":
          log("error", f"File {filename} not found on server")
          return
          
      filesize = int(filesize)
      current = 0
      
      # Receive the file
      with open(file_path, 'wb') as f:
          while current < filesize:
              data = clientSocket.recv(4096)
              if not data:
                  break
              hash_object.update(data)
              f.write(data)
              current += len(data)
              progress = (current / filesize) * 100  # Calculate progress
              log("info", f"Downloading: {progress:.2f}%")

              # Send progress to the Flask app
              requests.post('http://localhost:5000/update_progress', 
                           json={"filename": filename, "progress": progress})
              if filesize < 5 * 1024 * 1024:  
                  time.sleep(0.1) #delay for small files (<5MB) in order to be able to see the progress bar
      
      # Receive server's hash for verification
      server_hash = clientSocket.recv(64).decode()  # SHA-256 hash is 64 characters in hex
      client_hash = hash_object.hexdigest()
      
      if server_hash != client_hash:
          log('error', 'File integrity check failed during download')
          return
      
      # Send final 100% progress update
      requests.post('http://localhost:5000/update_progress', 
                   json={"filename": filename, "progress": 100})
    
                
    elif command == 3:
      log("info", "Requesting file list from server")
      #listing functionality
      data = clientSocket.recv(4096).decode()
      files_list = data.split(',')
      log("info", f"Received file list with {len(files_list)} files")
      return files_list 
      # Return the list to be used by Flask app

  except Exception as e:
    log("error", f"Error in client operation: {str(e)}")
    return [] if command == 3 else None
  finally:
    clientSocket.close()
    log("info", "Client connection closed")


if __name__ == "__main__":
    initiateClient(3)  # Fixed typo in function name