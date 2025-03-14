#web interface
from flask import *
from client import initiateClient

app = Flask(__name__)

@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Handle file upload
    # Get the file from the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    # Save the file temporarily
    filename = file.filename
    file.save(filename)
    
    # Call the client to upload the file
    initiateClient(1, filename)
    
    return jsonify({'success': True, 'message': f'File {filename} uploaded successfully'})

@app.route('/download', methods=['POST'])
def download():
    # Handle file download
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'})
    
    # Call the client to download the file
    initiateClient(2, filename)
    
    # In a real app, you'd return the file here
    return jsonify({'success': True, 'message': f'File {filename} downloaded'})

@app.route('/list', methods=['GET'])
def list_files():
    # Get the list of files from the server
    files_list = initiateClient(3)
    
    return jsonify({'files': files_list})

# using http methos POST/GET/... we recieve the frontend command and any additional data and then initiate client to use the TCP connection
if __name__ == '__main__':
    app.run(debug=True)
