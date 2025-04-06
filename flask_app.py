#web interface
from flask import *
from client import initiateClient
import os
from utils import log

app = Flask(__name__)
progress_data = {}

# Create client_files directory if it doesn't exist
CLIENT_FILES_DIR = "client_files"
if not os.path.exists(CLIENT_FILES_DIR):
    os.makedirs(CLIENT_FILES_DIR)

@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Handle file upload
        # Get the file from the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}) # checks the http request coming from the index.html if it has a field called file
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}) # incase there was no file to be uploaded then return an error to the frontend
        
        # Save the file temporarily in the client_files directory
        filename = file.filename
        file_path = os.path.join(CLIENT_FILES_DIR, filename)
        file.save(file_path)
        
        # Call the client to upload the file
        initiateClient(1, file_path) # calls our client socket to open connection with the server socket with method = 1 (meaning upload)
        
        return jsonify({'success': True, 'message': f'File {filename} uploaded successfully'}) # return to web interface a success mesage
    except Exception as e:
        log("error", f"Error during file upload: {str(e)}")
        return jsonify({'error': 'An error occurred during upload'})

@app.route('/download', methods=['POST'])
def download():
    try:
        # Handle file download
        filename = request.json.get('filename')
        if not filename:
            return jsonify({'error': 'No filename provided'})
        
        # Create a temporary file path for the download
        temp_file_path = os.path.join(CLIENT_FILES_DIR, f"temp_{filename}")
        
        # Call the client to download the file to a temporary location
        # Pass the original filename (without temp_ prefix) to the client
        initiateClient(2, temp_file_path, original_filename=filename)
        
        # Check if the file was downloaded successfully
        if not os.path.exists(temp_file_path):
            return jsonify({'error': 'File download failed'})
        
        # Stream the file to the user's browser and delete it afterward
        response = send_file(
            temp_file_path,
            as_attachment=True,
            download_name=filename
        )
        
        # Add a callback to delete the file after the response is sent
        @response.call_on_close
        def on_close():
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    log("info", f"Temporary file {temp_file_path} deleted after download")
            except Exception as e:
                log("error", f"Error deleting temporary file: {str(e)}")
        
        return response
    except Exception as e:
        log("error", f"Error during file download: {str(e)}")
        return jsonify({'error': 'An error occurred during download'})

@app.route('/list', methods=['GET'])
def list_files():
    try:
        # Get the list of files from the server
        files_list = initiateClient(3)
        return jsonify({'files': files_list})
    except Exception as e:
        log("error", f"Error during file listing: {str(e)}")
        return jsonify({'error': 'An error occurred while listing files'})

@app.route('/update_progress', methods=['POST'])
def update_progress():
    global progress_data
    data = request.json
    filename = data.get('filename', 'default_file')
    progress = data.get('progress', 0)
    
    # Update progress and status
    progress_data[filename] = {
        'progress': progress,
        'status': 'processing' if progress < 100 else 'completed'
    }
    
    print(f"Progress update for {filename}: {progress}%")
    return jsonify({"status": "success"})

@app.route('/get_progress/<filename>', methods=['GET'])
def get_progress(filename):
    # Return the progress for the specified filename
    if filename in progress_data:
        return jsonify(progress_data[filename])
    else:
        return jsonify({"progress": 0, "status": "unknown"})

# using http methos POST/GET/... we recieve the frontend command and any additional data and then initiate client to use the TCP connection
if __name__ == '__main__':
    app.run(debug=True)
