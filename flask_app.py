#web interface
from flask import *

app = Flask(__name__)

@app.route('/')
def mainPage():
    return render_template('index.html')

# using http methos POST/GET/... we recieve the frontend command and any additional data and then initiate client to use the TCP connection
if __name__ == '__main__':
    app.run(debug=True)
