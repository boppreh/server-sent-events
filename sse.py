from queue import Queue
from collections import defaultdict

class Publisher(object):
    """
    Contains a list of subscribers that can can receive updates.

    Each subscriber can have its own private data and may subscribe to
    different feeds.
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
        """
        Returns a generator of all subscribers in the given feeds.

        `feed` can either be a single feed name (e.g. "secret room") or a list
        of feed names (e.g. "['chat', 'global announcements']"). It defaults to
        the feed named "default feed".
        """
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
        # Note we call `str` here instead of leaving it to each subscriber's
        # `format` call. The reason is twofold: this caches the same between
        # subscribers, and is not prone to time differences.
        if callable(data):
            for queue, properties in self.get_subscribers(feed):
                value = data(properties)
                if value:
                    queue.put(str(value))
        else:
            for queue, _ in self.get_subscribers(feed):
                queue.put(str(data))

    def subscribe(self, feed='default feed', properties=None, initial_data=[]):
        """
        Subscribes to the channel, returning an infinite generator of
        Server-Sent-Events.

        Feed can either be a feed name (e.g. "secret room") or a list of feed
        names (e.g. "['chat', 'global messages']"). It defaults to the feed
        named "default feed".

        If `properties` is passed, these will be used for differentiation if a
        callable object is published (see `Publisher.publish`).

        If the list `initial_data` is passed, all data there will be sent
        before the regular feed process starts.
        """
        queue = Queue()
        properties = properties or {}
        subscriber = (queue, properties)

        for data in initial_data:
            queue.put(str(data))

        for subscribers_list in self._get_subscribers_lists(feed):
            subscribers_list.append(subscriber)

        while True:
            yield 'data: {}\n\n'.format(queue.get())

if __name__ == '__main__':
    import flask
    publisher = Publisher()

    app = flask.Flask(__name__, static_folder='static', static_url_path='')

    @app.route('/publish', methods=['POST'])
    def publish():
        sender_username = flask.request.form['username']
        message = flask.request.form['message']

        def m(subscriber_username):
            if subscriber_username != sender_username:
                return sender_username + ': ' + message

        publisher.publish(m)
        return ''

    @app.route('/subscribe')
    def subscribe():
        username = flask.request.args.get('username')
        return flask.Response(publisher.subscribe(properties=username),
                              content_type='text/event-stream')
    @app.route('/')
    def root():
        return app.send_static_file('chat.html')

    app.run(debug=True, threaded=True)
