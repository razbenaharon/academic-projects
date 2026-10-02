public class Action {
    private final Tile tile;

    private final Direction direction;

    public Action(Tile tile, Direction direction) {
        this.tile = tile;
        this.direction = direction;
    }

    public Direction getDirection() {
        return direction;
    }

    /**
     * The function returns a string that represents some movement on the board: into the string is inserted the
     * number that must be moved and the direction in which it must be moved.
     * @return The string that represents the movement.
     */
    public String toString() {
        String newString = "Move " + tile.getValue() + " " + direction.toString().toLowerCase();
        return newString;
    }
}