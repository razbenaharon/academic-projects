/**
 * Represents an interface for iterating over a filtered collection of songs.
 */
public interface FilteredSongIterable extends Iterable<Song> {
    /**
     * Filters the songs by artist name.
     *
     * @param artistName The artist name to filter by.
     */
    void filterArtist(String artistName);

    /**
     * Filters the songs by genre.
     *
     * @param genre The genre to filter by.
     */
    void filterGenre(Song.Genre genre);

    /**
     * Filters the songs by maximum duration.
     *
     * @param maxDuration The maximum duration to filter by.
     */
    void filterDuration(int maxDuration);
}