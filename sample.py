import flask
from datetime import datetime
from sse import Publisher

app = flask.Flask(__name__)
publisher = Publisher()

@app.route('/subscribe')
def subscribe():
    return flask.Response(publisher.subscribe(),
                          content_type='text/event-stream')

@app.route('/')
def root():
    ip = flask.request.remote_addr
    publisher.publish('New visit from {} at {}!'.format(ip, datetime.now()))

    return """
<html>
    <body>
        Open this page in new tabs to see the real time visits.
        <div id="events" />
        <script>
        var eventSource = new EventSource('/subscribe');
        eventSource.onmessage = function(e) {
            document.getElementById('events').innerHTML += e.data + '<br>';
        }
        </script>
    </body>
</html>
"""

app.run(debug=True, threaded=True)
