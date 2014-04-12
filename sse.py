from queue import Queue

class Subscriber(object):
    def __init__(self, properties=None):
        self.queue = Queue()
        self.properties = properties or {}

    def send(self, data):
        self.queue.put(str(data))

    def stream(self):
        while True:
            data = self.queue.get()
            print(data)
            yield 'data: {}\n\n'.format(data)

class Publisher(object):
    def __init__(self):
        self.subscribers = []

    def publish(self, data):
        if callable(data):
            for subscriber in self.subscribers:
                subscriber.send(data(subscriber.properties))
        else:
            for subscriber in self.subscribers:
                subscriber.send(data)

    def subscribe(self, properties=None):
        subscriber = Subscriber(properties)
        self.subscribers.append(subscriber)
        return subscriber.stream()

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
