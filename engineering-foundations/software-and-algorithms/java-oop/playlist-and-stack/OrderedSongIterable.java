/**
 * Represents an interface for iterating over a collection of songs in a specific order.
 */
public interface OrderedSongIterable extends Iterable<Song> {
    /**
     * Sets the scanning order for iterating over the songs.
     *
     * @param order The scanning order.
     */
    void setScanningOrder(ScanningOrder order);
}