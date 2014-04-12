from queue import Queue
from collections import defaultdict

class Publisher(object):
    """
    Contains a list of subscribers that can can receive updates.
    """
    def __init__(self):
        """
        Creates a new publisher with an empty list of subscribers.
        """
        self.subscribers_by_feed = defaultdict(list)

    def _get_subscribers_lists(self, feed):
        if isinstance(feed, str):
            yield self.subscribers_by_feed[feed]
        else:
            for feed_name in feed:
                yield self.subscribers_by_feed[feed_name]

    def get_subscribers(self, feed='default feed'):
        for subscriber_list in self._get_subscribers_lists(feed):
            yield from subscriber_list

    def publish(self, data, feed='default feed'):
        """
        Publishes data to all subscribers of the given feed.

        Feed can either be a feed name (e.g. "secret room") or a list of feed
        names (e.g. "['chat', 'global messages']"). It defaults to the feed
        named "default feed".

        If data is callable, the return of `data(properties)` will be published
        instead, for the `properties` object of each subscriber. This allows
        for subscriber differentiation.
        """
        if callable(data):
            for queue, properties in self.get_subscribers(feed):
                queue.put(data(properties))
        else:
            for queue, _ in self.get_subscribers(feed):
                queue.put(data)

    def subscribe(self, feed='default feed', properties=None):
        """
        Subscribes to the channel, returning an infinite generator of
        Server-Sent-Events.

        Feed can either be a feed name (e.g. "secret room") or a list of feed
        names (e.g. "['chat', 'global messages']"). It defaults to the feed
        named "default feed".

        If `properties` is passed, these will be used for differentiation if a
        callable object is published (see `Publisher.publish`).
        """
        queue = Queue()
        properties = properties or {}
        subscriber = (queue, properties)

        for subscribers_list in self._get_subscribers_lists(feed):
            subscribers_list.append(subscriber)

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
