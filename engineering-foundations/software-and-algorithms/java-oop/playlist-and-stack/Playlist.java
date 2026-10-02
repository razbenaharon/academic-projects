import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;

/**
 * Represents a playlist of songs.
 */
public class Playlist implements FilteredSongIterable, OrderedSongIterable, Cloneable {
    private List<Song> songsList;
    private ScanningOrder scanningOrder;
    private String filterArtist;
    private Song.Genre filterGenre;
    private int filterDuration;

    /**
     * Constructs an empty playlist.
     */
    public Playlist() {
        songsList = new ArrayList<>();
        scanningOrder = ScanningOrder.ADDING;
        filterDuration = Integer.MIN_VALUE;
    }

    /**
     * Returns a string representation of the playlist.
     *
     * @return The string representation of the playlist.
     */
    @Override
    public String toString() {
        String playlistString = "[";
        for (int i = 0; i < songsList.size(); i++) {
            playlistString += "(";
            playlistString += songsList.get(i);
            playlistString += ")";
            if (i < songsList.size() - 1) {
                playlistString += ", ";
            }
        }
        playlistString += "]";
        return playlistString;
    }

    /**
     * Checks if this playlist is equal to another object.
     *
     * @param other The object to compare.
     * @return true if the playlists are equal, false otherwise.
     */
    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (!(other instanceof Playlist)) {
            return false;
        }

        Playlist otherPlaylist = (Playlist) other;

        int playlistSize1 = this.songsList.size();
        int playlistSize2 = otherPlaylist.songsList.size();

        if (playlistSize1 != playlistSize2)
            return false;

        int equalCheck = 0;

        for (int i = 0; i < playlistSize1; i++) {
            for (int j = 0; j < playlistSize1; j++) {
                if (this.songsList.get(i).equals(otherPlaylist.songsList.get(j))) {
                    equalCheck++;
                    break;
                }
                if (j == playlistSize1 - 1)
                    return false;
            }
        }
        return true;
    }

    /**
     * Returns the hash code value for the playlist.
     *
     * @return The hash code value for the playlist.
     */
    @Override
    public int hashCode() {
        int result = 0;

        for (int i = 0; i < songsList.size(); i++) {
            result += songsList.get(i).hashCode();
        }
        return result;
    }

    /**
     * Creates and returns a deep copy of this playlist.
     *
     * @return A clone of this playlist.
     */
    @Override
    public Playlist clone() {
        try {
            Playlist clonedPlaylist = (Playlist) super.clone();
            clonedPlaylist.songsList = new ArrayList<>();

            for (Song song : this.songsList) {
                clonedPlaylist.songsList.add(song.clone());
            }

            return clonedPlaylist;
        } catch (CloneNotSupportedException e) {
            return null;
        }
    }

    /**
     * Adds a song to the playlist.
     *
     * @param song The song to be added.
     * @throws SongAlreadyExistsException If the song already exists in the playlist.
     */
    public void addSong(Song song) throws SongAlreadyExistsException {
        if (songsList.contains(song)) {
            throw new SongAlreadyExistsException();
        }
        songsList.add(song);
    }

    /**
     * Removes a song from the playlist.
     *
     * @param song The song to be removed.
     * @return true if the song was removed, false otherwise.
     */
    public boolean removeSong(Song song) {
        int playlistSize = songsList.size();
        int index = 0;
        for (index = 0; index < playlistSize; index++) {
            if (songsList.get(index).equals(song)) {
                songsList.remove(index);
                return true;
            }
        }
        return false;
    }

    /**
     * Sets the scanning order for iterating over the playlist.
     *
     * @param order The scanning order.
     */
    public void setScanningOrder(ScanningOrder order) {
        this.scanningOrder = order;
    }

    /**
     * Returns an iterator over the songs in the playlist.
     *
     * @return An iterator over the songs in the playlist.
     */
    public Iterator<Song> iterator() {
        return new PlaylistIterator();
    }

    /**
     * Filters the playlist by artist name.
     *
     * @param artistName The artist name to filter by.
     */
    @Override
    public void filterArtist(String artistName) {
        this.filterArtist = artistName;
    }

    /**
     * Filters the playlist by song genre.
     *
     * @param genre The genre to filter by.
     */
    @Override
    public void filterGenre(Song.Genre genre) {
        this.filterGenre = genre;
    }

    /**
     * Filters the playlist by maximum song duration.
     *
     * @param maxDuration The maximum duration to filter by.
     */
    @Override
    public void filterDuration(int maxDuration) {
        this.filterDuration = maxDuration;
    }

    /**
     * Represents an iterator over the songs in the playlist.
     */
    private class PlaylistIterator implements Iterator<Song> {
        private Iterator<Song> iterator;

        public PlaylistIterator() {
            List<Song> filteredSongs = new ArrayList<>(songsList);

            if (filterArtist != null) {
                filteredSongs.removeIf(song -> !song.getArtist().equals(filterArtist));
            }
            if (filterGenre != null) {
                filteredSongs.removeIf(song -> !song.getGenre().equals(filterGenre));
            }
            if (filterDuration != Integer.MIN_VALUE) {
                filteredSongs.removeIf(song -> song.getDuration() > filterDuration);
            }

            switch (scanningOrder) {
                case ADDING:
                    iterator = filteredSongs.iterator();
                    break;
                case NAME:
                    filteredSongs.sort(Comparator.comparing(Song::getName));
                    iterator = filteredSongs.iterator();
                    break;
                case DURATION:
                    filteredSongs.sort(Comparator.comparing(Song::getDuration));
                    iterator = filteredSongs.iterator();
                    break;
            }
        }

        /**
         * Checks if there is a next song in the playlist.
         *
         * @return true if there is a next song, false otherwise.
         */
        @Override
        public boolean hasNext() {
            return iterator.hasNext();
        }

        /**
         * Returns the next song in the playlist.
         *
         * @return The next song.
         */
        @Override
        public Song next() {
            return iterator.next();
        }
    }
}
