from collections import namedtuple

# Use this named tuple in your config.py to give your stations a name
URI = namedtuple("URI", "uri name")
uris = [URI('x-sonosapi-radio:<the_first_uri>', "Radio Station 1"),
        URI('x-sonosapi-radio:<the_second_uri>',  "Radio Station 2"),
        URI('x-sonos-spotify:<a_spotify_uri>', "My Cool Playlist"),
]

rooms = [("A room"),
         ("Some other room"),
         ("A room", "Some other room"),
         ("Room 3", "A room", "A different room entirely"),
]
