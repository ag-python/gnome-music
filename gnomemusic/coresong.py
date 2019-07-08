import gi
gi.require_version('Grl', '0.3')
from gi.repository import Grl, GLib, GObject

import gnomemusic.utils as utils


class CoreSong(GObject.GObject):
    """Exposes a Grl.Media with relevant data as properties
    """

    album = GObject.Property(type=str)
    album_disc_number = GObject.Property(type=int)
    artist = GObject.Property(type=str)
    duration = GObject.Property(type=int)
    media = GObject.Property(type=Grl.Media)
    grlid = GObject.Property(type=str, default=None)
    play_count = GObject.Property(type=int)
    state = GObject.Property()  # FIXME: How to set an IntEnum type?
    title = GObject.Property(type=str)
    track_number = GObject.Property(type=int)
    url = GObject.Property(type=str)

    def __init__(self, media, coreselection, grilo):
        super().__init__()

        self._grilo = grilo
        self._coreselection = coreselection
        self._favorite = False
        self._selected = False

        self.props.grlid = media.get_source() + media.get_id()
        self.update(media)

    def __eq__(self, other):
        return (isinstance(other, CoreSong)
                and other.props.media.get_id() == self.props.media.get_id())

    @GObject.Property(type=bool, default=False)
    def favorite(self):
        return self._favorite

    @favorite.setter
    def favorite(self, favorite):
        self._favorite = favorite

        # FIXME: Circular trigger, can probably be solved more neatly.
        old_fav = self.props.media.get_favourite()
        if old_fav == self._favorite:
            return

        self.props.media.set_favourite(self._favorite)
        self._grilo.writeback(self.props.media, Grl.METADATA_KEY_FAVOURITE)

    @GObject.Property(type=bool, default=False)
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self._selected == value:
            return

        self._selected = value
        self._coreselection.update_selection(self, self._selected)

    def update(self, media):
        self.props.media = media
        self.props.album = utils.get_album_title(media)
        self.props.album_disc_number = media.get_album_disc_number()
        self.props.artist = utils.get_artist_name(media)
        self.props.duration = media.get_duration()
        self.props.favorite = media.get_favourite()
        self.props.play_count = media.get_play_count()
        self.props.title = utils.get_media_title(media)
        self.props.track_number = media.get_track_number()
        self.props.url = media.get_url()

    def bump_play_count(self):
        self.props.media.set_play_count(self.props.play_count + 1)
        self._grilo.writeback(self.props.media, Grl.METADATA_KEY_PLAY_COUNT)

    def set_last_played(self):
        self.props.media.set_last_played(GLib.DateTime.new_now_utc())
        self._grilo.writeback(self.props.media, Grl.METADATA_KEY_LAST_PLAYED)
