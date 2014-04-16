from queue import Queue
from collections import defaultdict

class Publisher(object):
    """
    Contains a list of subscribers that can can receive updates.

    Each subscriber can have its own private data and may subscribe to
    different channel.
    """
    END_STREAM = {}

    def __init__(self):
        """
        Creates a new publisher with an empty list of subscribers.
        """
        self.subscribers_by_channel = defaultdict(list)

    def _get_subscribers_lists(self, channel):
        if isinstance(channel, str):
            yield self.subscribers_by_channel[channel]
        else:
            for channel_name in channel:
                yield self.subscribers_by_channel[channel_name]

    def get_subscribers(self, channel='default channel'):
        """
        Returns a generator of all subscribers in the given channel.

        `channel` can either be a channel name (e.g. "secret room") or a list
        of channel names (e.g. "['chat', 'global messages']"). It defaults to
        the channel named "default channel".
        """
        for subscriber_list in self._get_subscribers_lists(channel):
            yield from subscriber_list

    def _publish_single(self, data, queue):
        """
        Publishes a single piece of data to a single user. Data is encoded as
        required.
        """
        str_data = str(data)
        for line in str_data.split('\n'):
            queue.put('data: {}\n'.format(line))
        queue.put('\n')

    def publish(self, data, channel='default channel'):
        """
        Publishes data to all subscribers of the given channel.

        `channel` can either be a channel name (e.g. "secret room") or a list
        of channel names (e.g. "['chat', 'global messages']"). It defaults to
        the channel named "default channel".

        If data is callable, the return of `data(properties)` will be published
        instead, for the `properties` object of each subscriber. This allows
        for customized events.
        """
        # Note we call `str` here instead of leaving it to each subscriber's
        # `format` call. The reason is twofold: this caches the same between
        # subscribers, and is not prone to time differences.
        if callable(data):
            for queue, properties in self.get_subscribers(channel):
                value = data(properties)
                if value:
                    self._publish_single(value, queue)
        else:
            for queue, _ in self.get_subscribers(channel):
                self._publish_single(data, queue)

    def subscribe(self, channel='default channel', properties=None, initial_data=[]):
        """
        Subscribes to the channel, returning an infinite generator of
        Server-Sent-Events.

        `channel` can either be a channel name (e.g. "secret room") or a list
        of channel names (e.g. "['chat', 'global messages']"). It defaults to
        the channel named "default channel".

        If `properties` is passed, these will be used for differentiation if a
        callable object is published (see `Publisher.publish`).

        If the list `initial_data` is passed, all data there will be sent
        before the regular channel process starts.
        """
        queue = Queue()
        properties = properties or {}
        subscriber = (queue, properties)

        for data in initial_data:
            self._publish_single(data, queue)

        for subscribers_list in self._get_subscribers_lists(channel):
            subscribers_list.append(subscriber)

        return self._make_generator(queue)

    def _make_generator(self, queue):
        """
        Returns a generator that reads data from the queue, emitting data
        events, while the Publisher.END_STREAM value is not received.
        """
        while True:
            data = queue.get()
            if data is Publisher.END_STREAM:
                return
            yield data


    def close(self):
        """
        Closes all active subscriptions.
        """
        for channel in self.subscribers_by_channel.values():
            for queue, _ in channel:
                queue.put(Publisher.END_STREAM)
            channel.clear()


if __name__ == '__main__':
    # Starts an example chat application.
    # Run this module and point your browser to http://localhost:5000

    import cgi
    import flask
    publisher = Publisher()

    app = flask.Flask(__name__, static_folder='static', static_url_path='')

    @app.route('/publish', methods=['POST'])
    def publish():
        sender_username = flask.request.form['username']
        chat_message = flask.request.form['message']

        template = '<strong>{}</strong>: {}'
        full_message = template.format(cgi.escape(sender_username),
                                       cgi.escape(chat_message))

        def m(subscriber_username):
            if subscriber_username != sender_username:
                return full_message
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
