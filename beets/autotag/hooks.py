# This file is part of beets.
# Copyright 2013, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Glue between metadata sources and the matching logic."""
import logging
from collections import namedtuple

from beets import plugins
from beets import config

log = logging.getLogger('beets')


# Classes used to represent candidate options.

class AlbumInfo(object):
    """Describes a canonical release that may be used to match a release
    in the library. Consists of these data members:

    - ``album``: the release title
    - ``album_id``: MusicBrainz ID; UUID fragment only
    - ``artist``: name of the release's primary artist
    - ``artist_id``
    - ``tracks``: list of TrackInfo objects making up the release
    - ``asin``: Amazon ASIN
    - ``albumtype``: string describing the kind of release
    - ``va``: boolean: whether the release has "various artists"
    - ``year``: release year
    - ``month``: release month
    - ``day``: release day
    - ``label``: music label responsible for the release
    - ``mediums``: the number of discs in this release
    - ``artist_sort``: name of the release's artist for sorting
    - ``releasegroup_id``: MBID for the album's release group
    - ``catalognum``: the label's catalog number for the release
    - ``script``: character set used for metadata
    - ``language``: human language of the metadata
    - ``country``: the release country
    - ``albumstatus``: MusicBrainz release status (Official, etc.)
    - ``media``: delivery mechanism (Vinyl, etc.)
    - ``albumdisambig``: MusicBrainz release disambiguation comment
    - ``artist_credit``: Release-specific artist name

    The fields up through ``tracks`` are required. The others are
    optional and may be None.
    """
    def __init__(self, album, album_id, artist, artist_id, tracks, asin=None,
                 albumtype=None, va=False, year=None, month=None, day=None,
                 label=None, mediums=None, artist_sort=None,
                 releasegroup_id=None, catalognum=None, script=None,
                 language=None, country=None, albumstatus=None, media=None,
                 albumdisambig=None, artist_credit=None):
        self.album = album
        self.album_id = album_id
        self.artist = artist
        self.artist_id = artist_id
        self.tracks = tracks
        self.asin = asin
        self.albumtype = albumtype
        self.va = va
        self.year = year
        self.month = month
        self.day = day
        self.label = label
        self.mediums = mediums
        self.artist_sort = artist_sort
        self.releasegroup_id = releasegroup_id
        self.catalognum = catalognum
        self.script = script
        self.language = language
        self.country = country
        self.albumstatus = albumstatus
        self.media = media
        self.albumdisambig = albumdisambig
        self.artist_credit = artist_credit

class TrackInfo(object):
    """Describes a canonical track present on a release. Appears as part
    of an AlbumInfo's ``tracks`` list. Consists of these data members:

    - ``title``: name of the track
    - ``track_id``: MusicBrainz ID; UUID fragment only
    - ``artist``: individual track artist name
    - ``artist_id``
    - ``length``: float: duration of the track in seconds
    - ``index``: position on the entire release
    - ``medium``: the disc number this track appears on in the album
    - ``medium_index``: the track's position on the disc
    - ``artist_sort``: name of the track artist for sorting
    - ``disctitle``: name of the individual medium (subtitle)
    - ``artist_credit``: Recording-specific artist name

    Only ``title`` and ``track_id`` are required. The rest of the fields
    may be None. The indices ``index``, ``medium``, and ``medium_index``
    are all 1-based.
    """
    def __init__(self, title, track_id, artist=None, artist_id=None,
                 length=None, index=None, medium=None, medium_index=None,
                 artist_sort=None, disctitle=None, artist_credit=None):
        self.title = title
        self.track_id = track_id
        self.artist = artist
        self.artist_id = artist_id
        self.length = length
        self.index = index
        self.medium = medium
        self.medium_index = medium_index
        self.artist_sort = artist_sort
        self.disctitle = disctitle
        self.artist_credit = artist_credit

AlbumMatch = namedtuple('AlbumMatch', ['distance', 'info', 'mapping',
                                       'extra_items', 'extra_tracks'])

TrackMatch = namedtuple('TrackMatch', ['distance', 'info'])


# Aggregation of sources.

def _get_source():
    """Load and return the data source specified in the beets
    config object.
    """
    name = config['import']['source'].get()
    plugins.load_plugins([name])
    return plugins.get_plugin(name)

def _album_for_id(album_id):
    """Get an album corresponding to a MusicBrainz release ID."""
    return _get_source().candidates(album_id=album_id)[0]

def _track_for_id(track_id):
    """Get an item for a recording MBID."""
    return _get_source().item_candidates(track_id=track_id)[0]

def _album_candidates(items, artist, album, va_likely):
    """Search for album matches. ``items`` is a list of Item objects
    that make up the album. ``artist`` and ``album`` are the respective
    names (strings), which may be derived from the item list or may be
    entered by the user. ``va_likely`` is a boolean indicating whether
    the album is likely to be a "various artists" release.
    """
    return _get_source().candidates(items, artist, album, va_likely)

def _item_candidates(item, artist, title):
    """Search for item matches. ``item`` is the Item to be matched.
    ``artist`` and ``title`` are strings and either reflect the item or
    are specified by the user.
    """
    return _get_source().item_candidates(item, artist, title)
