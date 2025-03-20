#multithreaded TCP file server code
from socket import *
from threading import *
import os

PORT = 8080
SERVER_FILES_DIR = "server_files"  # Directory to store uploaded files

# Create the directory if it doesn't exist
if not os.path.exists(SERVER_FILES_DIR):
    os.makedirs(SERVER_FILES_DIR)

def handle_client(con, addr):
    print(f"New connection from {addr}")
    command = con.recv(1024).decode()
    
    if command == "1":
        print("Upload request received")
        # Receive filename
        filename = con.recv(1024).decode()
        print(f"Receiving file: {filename}")
        
        # Create full path for saving
        file_path = os.path.join(SERVER_FILES_DIR, filename)
        
        # Handle duplicate filenames
        base_name, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            new_filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(SERVER_FILES_DIR, new_filename)
            counter += 1
        
        # Receive and save the file
        with open(file_path, 'wb') as f:
            while True:
                data = con.recv(1024)
                if not data or len(data) < 1024:  # Last packet might be smaller
                    f.write(data)
                    break
                f.write(data)
        
        print(f"File saved as: {os.path.basename(file_path)}")
        
    elif command == "2":
        print("Download request received")
        # Receive filename
        filename = con.recv(1024).decode()
        print(f"Client requested file: {filename}")
        
        file_path = os.path.join(SERVER_FILES_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File {filename} not found")
            con.send("FILE_NOT_FOUND".encode())
        else:
            # Send the file
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                while data:
                    con.send(data)
                    data = f.read(1024)
            print(f"File {filename} sent to client")
    
    elif command == "3":
        print("List files request received")
        # Get list of files in the server directory
        files_list = os.listdir(SERVER_FILES_DIR)
        # Send the list as a comma-separated string
        con.send(",".join(files_list).encode())
        print("File list sent to client")
    
    else:
        print(f"Unknown command: {command}")
    
    con.close()
    print(f"Connection with {addr} closed")

def startServer():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', PORT))
    serverSocket.listen(10)  # 10 clients in queue
    print(f"Server listening on port {PORT}...")
    
    while True:
        connectionSocket, address = serverSocket.accept()
        print(f"Connection established with {address}")
        clientthread = Thread(target=handle_client, args=(connectionSocket, address))
        clientthread.daemon = True  # Make thread exit when main thread exits
        clientthread.start()

if __name__ == "__main__":
    print(f"Server starting on port {PORT}...")
    startServer()