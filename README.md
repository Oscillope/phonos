# phonos

A hardware Sonos controller which harkens back to a simpler time.

### Configuration

In order for this to work, you need a file called `config.py` in the same directory as phonos. It should have an array called `uris` of named tuples in it, which contains a list of up to 10 Sonos URIs (stations, songs, albums, whatever), as well as human-readable names for the stations. See the [SoCo documentation](http://docs.python-soco.com/en/latest/index.html) for more details about URIs. See the example config.py in this repo for an example of the named tuple format.

More configuration bits may be added in the future.

### Phone setup/wiring

TODO
