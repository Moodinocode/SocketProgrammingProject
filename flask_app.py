#web interface
from flask import Flask

app = Flask(__name__)

# @app.route('/')
# def hello():
#     return render_template('index.html')
@app.route('/')
def MainPage():
    return '''
      <html>
        <head>
          <title>File Sharing</title>
        </head>
        <body>
          <h1>Hello, World!</h1>
          <button>Uplaod</button>
          <button>Download</button>
          <button>List</button>
          <p>Welcome to my Flask application.</p>
        </body>
      </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
