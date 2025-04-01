#web interface
from flask import *
from client import initiateClient

app = Flask(__name__)

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
        
        # Save the file temporarily
        filename = file.filename
        file.save(filename)
        
        # Call the client to upload the file
        initiateClient(1, filename) # calls our client socket to open connection with the server socket with method = 1 (meaning upload)
        
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
        
        # Call the client to download the file
        initiateClient(2, filename)
        
        # Call the client to download the file
        return jsonify({'success': True, 'message': f'File {filename} downloaded'})
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
    progress_data = request.json
    # Store the progress data (you can use a filename or user ID as a key)
    # For example, using a static key for demonstration
    progress_data['filename'] = progress_data.get('filename', 'default_file')
    progress_data[progress_data['filename']] = progress_data['progress']
    print(f"Progress update: {progress_data['progress']}%")
    return jsonify({"status": "success"})

@app.route('/get_progress/<filename>', methods=['GET'])
def get_progress(filename):
    # Return the progress for the specified filename
    return jsonify({"progress": progress_data.get(filename, 0)})

# using http methos POST/GET/... we recieve the frontend command and any additional data and then initiate client to use the TCP connection
if __name__ == '__main__':
    app.run(debug=True)
