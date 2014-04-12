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

`Publish()`
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
