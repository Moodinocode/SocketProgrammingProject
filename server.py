#multithreaded TCP file server code
from socket import *
from threading import *
import os
import hashlib

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
            hash_object = hashlib.sha256()

            # Handle duplicate filenames
            base_name, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{extension}"
                file_path = os.path.join(SERVER_FILES_DIR, new_filename)
                counter += 1
            
            with open(file_path, 'wb') as f:
                total_received = 0
                while True:
                    data = con.recv(4096)
                    if not data:
                        break
                    hash_object.update(data)
                    f.write(data)
                    total_received += len(data)
                    if len(data) < 4096:  # Last packet might be smaller
                        break
                
                log("info", f"Received {total_received} bytes for file {filename}")
            
            # Receive client's hash for verification
            client_hash = con.recv(64).decode()  # SHA-256 hash is 64 characters in hex
            server_hash = hash_object.hexdigest()
            
            if client_hash == server_hash:
                con.send("OK".encode())
                log("info", f"{filename} file saved successfully with integrity verified")
            else:
                con.send("FAIL".encode())
                log("error", f"File integrity check failed for {filename}")
                # Optionally remove the corrupted file
                os.remove(file_path)
                return
        
        elif command == "2":
            log("info", "Download request received")

            # Receive filename
            filename = con.recv(1024).decode()
            log("info",f"Client requested file: {filename}")
            
            # Strip 'temp_' prefix if it exists
            if filename.startswith("temp_"):
                original_filename = filename[5:]  # Remove the 'temp_' prefix
                log("info", f"Stripped 'temp_' prefix, using: {original_filename}")
                filename = original_filename

            file_path = os.path.join(SERVER_FILES_DIR, filename)
            
            #check if file exists
            if not os.path.exists(file_path):
                log("warning", f"File {filename} not found")
                con.send("FILE_NOT_FOUND".encode())
                return
            else:
                #send the file in raw bits
                filesize = os.path.getsize(file_path)  # sending the file size in order to know the progress overall
                con.send(str(filesize).encode())  # Send file size
                
                # For large files like MOV, we need to handle the transfer differently
                with open(file_path, 'rb') as f:
                    total_sent = 0
                    hash_object = hashlib.sha256()
                    while True:
                        data = f.read(4096)  # Increased buffer size for better performance
                        if not data:
                            break
                        hash_object.update(data)
                        con.send(data)
                        total_sent += len(data)

                # Send the hash to client for verification
                con.send(hash_object.hexdigest().encode())
                
                log("info", f"Sent {total_sent} bytes for file {filename}")
                log("info", f"File {filename} sent to client with integrity verification")
        
        elif command == "3":
            log("info", "List files request received")
            # Get list of files in the server directory
            files_list = os.listdir(SERVER_FILES_DIR)
            # Send the list as a comma-separated string
            con.send(",".join(files_list).encode())
            log("info", "File list sent to client")
            
        elif command == "4":
            log("info", "Delete file request received")
            
            # Receive filename
            filename = con.recv(1024).decode()
            log("info", f"Client requested to delete file: {filename}")
            
            file_path = os.path.join(SERVER_FILES_DIR, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                log("warning", f"File {filename} not found for deletion")
                con.send("FILE_NOT_FOUND".encode())
                return
            else:
                try:
                    # Delete the file
                    os.remove(file_path)
                    log("info", f"File {filename} deleted successfully")
                    con.send("SUCCESS".encode())
                except Exception as e:
                    log("error", f"Error deleting file {filename}: {str(e)}")
                    con.send("ERROR".encode())
        
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