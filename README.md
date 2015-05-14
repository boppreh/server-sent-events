server-sent-events
==================

This small modules implements a `Publisher` class to handle events in the HTTP
Server-Sent-Events protocol.

It allows a number of subscribers to get notifications when events happen in
certain feed channels. The common use case is for a Javascript client to
subscribe to these feed using an `EventSource` instance, and the events be sent
by a Python server like `Flask`.

You can run the module as a Python script to start an example chat, available
at http://localhost:5000 .


Features
========

- Simple `Publisher` with `publish` and `subscribe` methods

- Optional channels support

- Optional subscriber differentiation (subscribers have individual properties
  that can be used to generate custom events)

- Optional initial data for subscribers

- Server type agnostic


API Overview
============

`Publisher()`
-----------
Creates a new publisher with an empty list of subscribers. All following
functions are methods of Publisher.


`subscribe(channel='default channel', properties=None, initial_data=[])`
------------------------------------------------------------------------
Subscribes to the channel(s), returning an infinite generator of
Server-Sent-Events.

If `properties` is passed, these will be used for differentiation if a
callable object is published (see `Publisher.publish`).

If the list `initial_data` is passed, all data there will be sent
before the regular channel process starts.


`publish(data, channel='default channel')`
------------------------------------------------
Publishes data to all subscribers of the given channel(s).

If data is callable, the return of `data(properties)` will be published
instead, for the `properties` object of each subscriber. This allows
for customized events.


`get_subscribers(channel='default channel')`
--------------------------------------------------
Returns a generator of all subscribers in the given channel(s).


Note on `channel`
-----------------

`channel` can either be a channel name (e.g. `'secret room'`) or a list
of channel names (e.g. `['chat', 'global messages']`). It defaults to
the channel named `'default channel'`.


Example
=======

This is a minimal example using Flask as the server. Every viewer receives a
notification when a new viewer visits the page. Open many simultaneous tabs to
see the result.

For simplicity reasons it uses threads to serve the event streams. To build
actual products you probably want to use gevents/gunicorn.

```Python
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
```

This example can be run at `sample.py`.
