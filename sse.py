import flask

app = flask.Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def root():
    pass

if __name__ == '__main__':
    app.run(debug=True)
