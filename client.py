"""
TCP File Transfer Client Library

This module provides the client-side implementation for the file sharing system.
It establishes socket connections to the server and implements file upload, download,
listing, and deletion operations with progress tracking and integrity verification.

Each operation creates a new socket connection, performs the requested operation
according to the protocol specification, and then closes the connection.
"""
from socket import *
import os
import requests
import time
from utils import log, interrupted_downloads_tracker
import hashlib
from tqdm import tqdm

PORT = 8080
ServerIP = "127.0.0.1"  # Use localhost

def initiateClient(command, file_path=None, original_filename=None, filename=None, user_id=None, is_overwrite=False): #command should be sent from the flask web app
  """
  Establish a connection to the server and perform the requested file operation.
  
  This function is the main API for client-server communication. It handles
  all aspects of the custom file transfer protocol including command transmission,
  file data exchange, and integrity verification.
  
  Protocol Commands:
      1: Upload - Send a file to the server
      2: Download - Retrieve a file from the server
      3: List - Get a list of all files on the server
      4: Delete - Remove a file from the server (admin only)
  
  Parameters:
      command (int): The operation code (1=upload, 2=download, 3=list, 4=delete)
      file_path (str, optional): Local path for the file to upload or download location
      original_filename (str, optional): Original name of file for download (without temp_ prefix)
      filename (str, optional): Name of file to delete when using command 4
      user_id (int, optional): User ID for tracking interrupted downloads
      is_overwrite (bool, optional): Flag to indicate if upload should overwrite existing file
  
  Returns:
      list or str or None: For command 3 (list), returns list of filenames
                          For command 4 (delete), returns status string
                          For commands 1 and 2, returns None
  
  Raises:
      Exception: Logs but does not raise exceptions to caller
  """
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
      
      # Send the overwrite flag
      overwrite_str = str(is_overwrite).lower()
      clientSocket.send(overwrite_str.encode())
      log("info", f"Sending overwrite flag: {overwrite_str}")
      
      if is_overwrite:
         log("info",f"{user_id} is requesting to overwrite {filename}")
      
      hash_object = hashlib.sha256()
      
      #sending the contents of the file
      with open(file_path, 'rb') as f:
          total_size = os.path.getsize(file_path)
          pbar = tqdm(total=total_size,desc="Uploading") # initializing terminal progress bar
          sent = 0
          data = f.read(4096)
          while data:
              # Calculate SHA-256 hash during file transfer for integrity verification
              hash_object.update(data)
              clientSocket.send(data)
              sent += len(data)
              progress = (sent / total_size) * 100
              pbar.update(4096) #updating terminal progress bar

              # Update progress tracking for UI display
              requests.post('http://localhost:5000/update_progress', 
                           json={"filename": filename, "progress": progress})
              data = f.read(4096)
              # if total_size < 5 * 1024 * 1024:  
              #     time.sleep(0.1) #delay for small files (<5MB) in order to be able to see the progress bar 
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
      
      # Interrupted download tracking (partial implementation)
      interrupted_downloads_tracker.setdefault(user_id, {}).setdefault(filename, 0)
      offset = interrupted_downloads_tracker[user_id][filename] % int(filesize)
      # above implementation might lead to weird error
      #offset = min(interrupted_downloads_tracker[user_id][filename], int(filesize))
      #
      clientSocket.send(str(offset).encode())

      if filesize == "FILE_NOT_FOUND":
          log("error", f"File {filename} not found on server")
          return
          
      filesize = int(filesize)
      #if offset>=filesize:
      #  offset = 0
      #  interrupted_downloads_tracker[user_id][filename] = 0
      current = offset
      #mode = 'wb' if offset == 0 else 'r+b' 
      # Receive the file
      with tqdm(total=filesize, initial=offset, desc="Downloading", unit="B", unit_scale=True) as pbar:  # initializing terminal progress bar
  #      with open(file_path, mode) as f:
        with open(file_path, 'wb') as f:
            while current < filesize:
                to_read = min(4096, filesize - current)
                data = clientSocket.recv(to_read) # this is done not to ingulf the hash within in the file
                if not data:
                    break
                hash_object.update(data)
                f.write(data)
                current += len(data)
                #interrupted_downloads_tracker[user_id][filename] = current
                #log("info",f"incase of intrupption we are at byte {interrupted_downloads_tracker[user_id][filename]}")
                progress = (current / filesize) * 100  # Calculate progress
                pbar.update(len(data)) #updating terminal progress bar
                log("info", f"Downloading: {progress:.2f}%") # logging the progress before sending it to web interface

                # Update progress tracking for UI display
                requests.post('http://localhost:5000/update_progress', 
                            json={"filename": filename, "progress": progress})
                # if filesize < 5 * 1024 * 1024:  
                #     time.sleep(0.1) #delay for small files (<5MB) in order to be able to see the progress bar
      
      # Receive server's hash for verification
      server_hash = clientSocket.recv(64).decode()  # SHA-256 hash is 64 characters in hex
      log('info', f'hash recieved during download from server in hex is {server_hash}')

      client_hash = hash_object.hexdigest()
      log('info', f'hash calculated during download from client in hex is {client_hash}')

      # Verify file integrity after download
      if server_hash != client_hash:
          log('error', 'File integrity check failed during download')
          return
      else:
         log("info",f"file {filename} recived successfully with file integrity verified")
      
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
      
    elif command == 4:
      if not filename:
        log("error", "No filename provided for deletion")
        return "ERROR"
        
      log("info", f"Deleting file: {filename}")
      
      # Send the filename to delete
      clientSocket.send(filename.encode())
      
      # Receive the result from the server
      result = clientSocket.recv(1024).decode()
      log("info", f"Delete result: {result}")
      
      return result

  except Exception as e:
    log("error", f"Error in client operation: {str(e)}")
    return [] if command == 3 else None
  finally:
    clientSocket.close()
    log("info", "Client connection closed")


if __name__ == "__main__":
    initiateClient(3)  # Fixed typo in function name