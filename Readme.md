# Advanced File Sharing System

This is a project Done for the CSC 430 (Computer Networks) Course by: Mohamad Mehdi and Mounir Nawwar

A multithreaded TCP socket-based client-server application that enables secure file transfers with integrity verification, version control, and a web interface.

## System Architecture

- **Server:** Multithreaded TCP socket server (port 8080) with SHA-256 integrity verification
- **Client:** Socket-based client library with progress tracking
- **Web Interface:** Flask application with user authentication and AJAX progress updates
- **Storage:** Separate directories for server and client files with versioning support

## Features

### Core Features
- File Upload with integrity verification
- File Download with progress tracking
- File Listing
- Automatic file versioning for duplicates (filename_1, filename_2, etc.)
- SHA-256 hash verification for all file transfers
- Comprehensive logging system
- Role-based access control

### Admin-specific Features
- File deletion
- Log viewing
- File overwrite capability

## Setup and Running Instructions

1. Open a terminal and navigate to the project directory:

   ```
   cd ...\SocketProgrammingProject\
   ```

2. Install the required libraries:

   ```
   pip install -r requirements.txt
   ```

3. Start the server:

   ```
   python server.py
   ```

4. Open another terminal in the same directory and start the Flask application:

   ```
   python flask_app.py
   ```

5. Access the web interface by navigating to:

   ```
   http://127.0.0.1:5000
   ```

## Available Users

### Admin User
- Username: `admin`
- Password: `admin123`

### Normal Users
1. Username: `Ayman Tajeddine`
   - Password: `networksOnTop`
2. Username: `Mohammad Jomha`
   - Password: `CP3ezA`
3. Username: `Alice`
   - Password: `whereIsBob`

## Technical Details

### Custom File-Sharing Protocol
The system uses a custom request-response protocol over TCP sockets with the following commands:
- Command 1: UPLOAD - Send file to server with hash verification
- Command 2: DOWNLOAD - Retrieve file from server with hash verification
- Command 3: LIST - Get a list of files from the server
- Command 4: DELETE - Remove a file from the server (admin only)

### Integrity Verification
All file transfers include SHA-256 hash verification to ensure data integrity. Corrupted files are automatically detected and removed.

### Project Structure
- `server.py` - Multithreaded TCP file server
- `client.py` - Socket-based client library
- `flask_app.py` - Web interface with user authentication
- `utils.py` - Shared logging and tracking utilities
- `server_files/` - File storage on server side
- `client_files/` - Temporary storage for client operations
