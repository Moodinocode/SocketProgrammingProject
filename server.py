#multithreaded TCP file server code
from socket import *
from threading import *
import os

from utils import log

PORT = 8080
SERVER_FILES_DIR = "server_files"  # Directory to store uploaded files

# Create the directory if it doesn't exist
if not os.path.exists(SERVER_FILES_DIR):
    os.makedirs(SERVER_FILES_DIR)

def handle_client(con, addr):
    try:
        log("info", f"New serving socket connected to address = {addr}")
        command = con.recv(1024).decode()
        
        if command == "1":
            log("info", f"Upload request received")
            
            # Receive filename
            filename = con.recv(1024).decode()
            log("info", f"Receiving file with name: {filename}")
            
             # Create full path for saving the files
            file_path = os.path.join(SERVER_FILES_DIR, filename)

            # Handle duplicate filenames
            base_name, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{extension}"
                file_path = os.path.join(SERVER_FILES_DIR, new_filename)
                counter += 1
            
            with open(file_path, 'wb') as f:
                while True:
                    data = con.recv(1024)
                    if not data or len(data) < 1024: # Last packet might be smaller
                        f.write(data)
                        break
                    f.write(data)
            
            log("info", f"{filename} file saved on: {os.path.basename(file_path)}")
        
        elif command == "2":
            log("info", "Download request received")

            # Receive filename
            filename = con.recv(1024).decode()
            log("info",f"Client requested file: {filename}")

            file_path = os.path.join(SERVER_FILES_DIR, filename)
            
            #check if file exists
            if not os.path.exists(file_path):
                log("warning", f"File {filename} not found")
                con.send("FILE_NOT_FOUND".encode())
            else:
                #send the file in raw bits
                filesize = os.path.getsize(file_path)  # sending the file size in order to know the progress overall
                con.send(str(filesize).encode())  # Send file size
                with open(file_path, 'rb') as f:
                    data = f.read(1024)
                    while data:
                        con.send(data)
                        data = f.read(1024)
                log("info", f"File {filename} sent to client")
        
        elif command == "3":
            log("info", "List files request received")
            # Get list of files in the server directory
            files_list = os.listdir(SERVER_FILES_DIR)
            # Send the list as a comma-separated string
            con.send(",".join(files_list).encode())
            log("info", "File list sent to client")
        
        else:
            log("warning", f"Unknown command: {command}")
    
    except Exception as e:
        log("error", f"Error handling client {addr}: {str(e)}")
    
    finally:
        con.close()
        log("info", f"Connection with {addr} closed")

def startServer():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', PORT))
    serverSocket.listen(10)  # 10 clients in queue
    log("info",f"Server listening on port {PORT}...")
    
    while True:
        connectionSocket, address = serverSocket.accept()
        log("info",f"New connection established with client of address = {address}")
        clientthread = Thread(target=handle_client, args=(connectionSocket, address))
        clientthread.daemon = True  # Make thread exit when main thread exits
        clientthread.start()

if __name__ == "__main__":
    log("info",f"Server starting on port {PORT}...")
    startServer()