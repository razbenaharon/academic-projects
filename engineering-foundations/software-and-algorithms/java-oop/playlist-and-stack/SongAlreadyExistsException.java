/**
 * Exception thrown when a song already exists in the playlist.
 */
public class SongAlreadyExistsException extends RuntimeException {
    /**
     * Constructs a SongAlreadyExistsException with a default error message.
     */
    public SongAlreadyExistsException() {
        super("The song already exists in the playlist.");
    }
}