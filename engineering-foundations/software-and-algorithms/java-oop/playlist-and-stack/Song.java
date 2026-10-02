/**
 * Represents a song.
 */
public class Song implements Cloneable {
    private String name;
    private String artist;
    private Genre genre;
    private int duration;

    /**
     * Enumerates the genres of a song.
     */
    public enum Genre {
        POP,
        ROCK,
        HIP_HOP,
        COUNTRY,
        JAZZ,
        DISCO
    }

    /**
     * Constructs a Song object with the specified name, artist, genre, and duration.
     *
     * @param name     The name of the song.
     * @param artist   The artist of the song.
     * @param genre    The genre of the song.
     * @param duration The duration of the song in seconds.
     */
    public Song(String name, String artist, Genre genre, int duration) {
        this.name = name;
        this.artist = artist;
        this.genre = genre;
        this.duration = duration;
    }

    /**
     * Retrieves the name of the song.
     *
     * @return The name of the song.
     */
    public String getName() {
        return name;
    }

    /**
     * Sets the name of the song.
     *
     * @param name The name of the song.
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Retrieves the artist of the song.
     *
     * @return The artist of the song.
     */
    public String getArtist() {
        return artist;
    }

    /**
     * Sets the artist of the song.
     *
     * @param artist The artist of the song.
     */
    public void setArtist(String artist) {
        this.artist = artist;
    }

    /**
     * Retrieves the genre of the song.
     *
     * @return The genre of the song.
     */
    public Genre getGenre() {
        return genre;
    }

    /**
     * Sets the genre of the song.
     *
     * @param genre The genre of the song.
     */
    public void setGenre(Genre genre) {
        this.genre = genre;
    }

    /**
     * Retrieves the duration of the song.
     *
     * @return The duration of the song in seconds.
     */
    public int getDuration() {
        return duration;
    }

    /**
     * Sets the duration of the song.
     *
     * @param duration The duration of the song in seconds.
     */
    public void setDuration(int duration) {
        this.duration = duration;
    }

    /**
     * Returns a string representation of the song in the format: "name, artist, genre, duration".
     *
     * @return The string representation of the song.
     */
    @Override
    public String toString() {
        int numberOfMinutes = duration / 60;
        int numberOfSeconds = duration % 60;
        String durationString = String.valueOf(numberOfMinutes) + ":";

        if (numberOfSeconds < 10) {
            durationString += "0";
        }

        durationString += String.valueOf(numberOfSeconds);

        return name + ", " + artist + ", " + genre + ", " + durationString;
    }

    /**
     * Checks if this song is equal to another object.
     *
     * @param other The object to compare against.
     * @return true if the object is a Song and has the same name and artist, false otherwise.
     */
    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (!(other instanceof Song)) {
            return false;
        }

        Song otherSong = (Song) other;
        return (otherSong.name.equals(this.name) && otherSong.artist.equals(this.artist));
    }

    /**
     * Generates a hash code for the song.
     *
     * @return The hash code value for the song.
     */
    @Override
    public int hashCode() {
        int result = 17;

        for (int i = 0; i < this.name.length(); i++) {
            result += this.name.charAt(i) - 65;
            result *= i + 1;
        }
        result *= 35;

        for (int i = 0; i < this.artist.length(); i++) {
            result += this.artist.charAt(i) - 65;
            result *= i + 1;
        }

        return result;
    }

    /**
     * Creates a clone of the song.
     *
     * @return A cloned instance of the song.
     */
    @Override
    public Song clone() {
        try {
            Song clonedSong = (Song) super.clone();
            clonedSong.genre = this.genre;
            return clonedSong;
        } catch (CloneNotSupportedException e) {
            return null;
        }
    }
}
