import java.util.Arrays;

public class Board {
    private final Tile[][] tiles;

    private final Tile[][] solutionTiles;

    private final int[][] solutionTilesIndex;

    private final int boardNumberOfRows;

    private final int boardNumberOfColumns;

    private String boardString;

    public void updateString() {
        String newBoard = StringBoard.tilesToString(tiles, boardNumberOfRows, boardNumberOfColumns);
        this.boardString = newBoard;
    }
    /**
     The constructor of the board class receives a string of the game board and creates
     a 2D array of tiles corresponding to the given board and additionally
     creates a 2D array of tiles of the solution board.
     */
    public Board(String boardString) {
        int[][] boardArray = StringBoard.stringToArray(boardString);
        boardNumberOfRows = boardArray.length;
        boardNumberOfColumns = boardArray[0].length;
        this.tiles = new Tile[boardNumberOfRows][boardNumberOfColumns];
        for (int i = 0; i < boardNumberOfRows; i++) {
            for (int j = 0; j < boardNumberOfColumns; j++) {
                tiles[i][j] = new Tile(boardArray[i][j]);
            }
        }
        int counter = 1;
        this.solutionTiles = new Tile[boardNumberOfRows][boardNumberOfColumns];
        for (int i = 0; i < boardNumberOfRows; i++) {
            for (int j = 0; j < boardNumberOfColumns; j++) {
                solutionTiles[i][j] = new Tile(counter);
                counter++;
            }
        }
        solutionTiles[boardNumberOfRows - 1][boardNumberOfColumns - 1] = new Tile(0);
        this.solutionTilesIndex = new int[2][boardNumberOfRows * boardNumberOfColumns];
        int currentNumber = 0;
        for (int i = 0; i < boardNumberOfRows; i++) {
            for (int j = 0; j < boardNumberOfColumns; j++) {
                solutionTilesIndex[0][currentNumber] = i;
                solutionTilesIndex[1][currentNumber] = j;
                currentNumber++;
            }
        }
    }

    public int getBoardNumberOfRows() {
        return boardNumberOfRows;
    }

    public int getBoardNumberOfColumns() {
        return boardNumberOfColumns;
    }

    public String getBoardString() {
        return boardString;
    }

    public Tile[][] getTiles() {
        return tiles;
    }

    public Tile[][] getSolutionTiles() {
        return solutionTiles;
    }

    public int[][] getSolutionTilesIndex() {
        return solutionTilesIndex;
    }

    @Override
    public boolean equals(Object other) {
        if (!(other instanceof Board)) {
            return false;
        }
        Board board = (Board) other;
        return Arrays.deepEquals(this.tiles, board.tiles);
    }

    @Override
    public int hashCode() {
        return Arrays.deepHashCode(tiles);
    }
}