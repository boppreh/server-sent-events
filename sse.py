from queue import Queue

class Publisher(object):
    def __init__(self):
        self.subscribers = []

    def publish(self, data):
        if callable(data):
            for queue, properties in self.subscribers:
                queue.put(data(properties))
        else:
            for queue, _ in self.subscribers:
                queue.put(data)

    def subscribe(self, properties=None):
        queue = Queue()
        properties = properties or {}
        self.subscribers.append((queue, properties))
        while True:
            yield 'data: {}\n\n'.format(queue.get())

if __name__ == '__main__':
    import flask
    publisher = Publisher()

    app = flask.Flask(__name__, static_folder='static', static_url_path='')

    @app.route('/publish')
    def publish():
        data = flask.request.args.get('data')
        publisher.publish(data)
        return 'Sent ' + data

    @app.route('/subscribe')
    def subscribe():
        return flask.Response(publisher.subscribe(),
                              content_type='text/event-stream')

    @app.route('/')
    def index():
        return """
<html>
  <head>
  </head>
  <body>
    <h1>Server sent events</h1>
    <div id="event"></div>
    <script type="text/javascript">

    var eventOutputContainer = document.getElementById("event");
    var evtSrc = new EventSource("/subscribe");

    evtSrc.onmessage = function(e) {
        console.log(e.data);
        eventOutputContainer.innerHTML = e.data;
    };

    </script>
  </body>
</html>
        """

    app.run(debug=True, threaded=True)
