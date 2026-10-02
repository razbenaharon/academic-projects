public class State {
    private final Board board;

    private final Board solutionBoard;

    public State(Board board) {
        this.board = board;
        String solutionBoardString = StringBoard.tilesToString(this.board.getSolutionTiles(),
                board.getBoardNumberOfRows(), board.getBoardNumberOfColumns());
        this.solutionBoard = new Board(solutionBoardString);
    }

    /**
     * The function checks whether the current state in which the board is located is the target state,
     * that is, the state in which the board is completely solved. The function does this by checking that
     * each square is in the position where it should be in a solved board - this parameter is of course determined
     * by the dimensions of the board.
     * @return The function returns true if the current state is indeed the state in which the board is solved,
     * and false if the current state is not the solved board
     */
    public boolean isGoal() {
        int value = 1;
        for (int i = 0; i < board.getBoardNumberOfRows(); i++) {
            for (int j = 0; j < board.getBoardNumberOfColumns(); j++) {
                Tile tile = board.getTiles()[i][j];
                if (i == board.getBoardNumberOfRows() - 1 && j == board.getBoardNumberOfColumns() - 1) {
                    if (tile.getValue() != 0) {
                        return false;
                    }
                }
                else {
                    if (tile.getValue() != value) {
                        return false;
                    }
                }
                value++;
            }
        }
        return true;
    }

    /**
     * The function checks which moves can be made in the current state. The function checks this by checking the
     * position of the zero coordinate, i.e., the empty slot on the board. If the square is inside the board and not
     * at the edges, then you can move any of the four numbers around it. But, if the cube is on one of the edges,
     * you cannot move a number that is after the edge. For example, if the empty square is in the upper left corner,
     * we cannot move a number that is above or to the left of the empty square. After we have found the possible
     * moves we mark it by boolean flags. After that we create an Actions type array where each cell marks a
     * possible action and we insert the corresponding Action into each cell in the array in a certain order. Do not
     * leave empty cells in the array, therefore we check its size according to the number of flags marked as true
     * @return The function returns an array of type Action where each cell in the array represents a possible action
     */
    public Action[] actions() {
        int flagIsLegalUp = 0, flagIsLegalDown = 0, flagIsLegalRight = 0,
                flagIsLegalLeft = 0, indexOfRowOfBlankTile = 0, indexOfColumnOfBlankTile = 0;
        for (int i = 0; i < board.getBoardNumberOfRows(); i++) {
            for (int j = 0; j < board.getBoardNumberOfColumns(); j++) {
                if (board.getTiles()[i][j].getValue() == 0) {
                    indexOfRowOfBlankTile = i;
                    indexOfColumnOfBlankTile = j;
                    break;
                }
            }
        }
        if (indexOfRowOfBlankTile != board.getBoardNumberOfRows() - 1) {
            flagIsLegalUp = 1;
        }
        if (indexOfRowOfBlankTile != 0) {
            flagIsLegalDown = 1;
        }
        if (indexOfColumnOfBlankTile != 0) {
            flagIsLegalRight = 1;
        }
        if (indexOfColumnOfBlankTile != board.getBoardNumberOfColumns() - 1) {
            flagIsLegalLeft = 1;
        }
        int size = 0;
        size = flagIsLegalUp + flagIsLegalDown + flagIsLegalRight + flagIsLegalLeft;
        Action[] actions = new Action[size];
        int index = 0, location = 0;
        while (location < size) {
            int coordinationOfRow = indexOfRowOfBlankTile, coordinationOfCol = indexOfColumnOfBlankTile;
            if (index == 0) {
                if (flagIsLegalUp == 1) {
                    coordinationOfRow++;
                    actions[location] = new Action(board.getTiles()[coordinationOfRow][coordinationOfCol],
                            Direction.UP);
                    actions[location].toString();
                    location++;
                }
            }
            else if (index == 1) {
                if (flagIsLegalDown == 1) {
                    coordinationOfRow--;
                    actions[location] = new Action(board.getTiles()[coordinationOfRow][coordinationOfCol],
                            Direction.DOWN);
                    actions[location].toString();
                    location++;
                }
            }
            else if (index == 2) {
                if (flagIsLegalRight == 1) {
                    coordinationOfCol--;
                    actions[location] = new Action(board.getTiles()[coordinationOfRow][coordinationOfCol],
                            Direction.RIGHT);
                    actions[location].toString();
                    location++;
                }
            }
            else if (index == 3) {
                if (flagIsLegalLeft == 1) {
                    coordinationOfCol++;
                    actions[location] = new Action(board.getTiles()[coordinationOfRow][coordinationOfCol],
                            Direction.LEFT);
                    actions[location].toString();
                    location++;
                }
            }
            index++;
        }
        return actions;
    }

    /**
     * The function receives an Action and creates a new array that will represent the new state of
     * the board after the action is performed. A classification will be made according to the type of operation
     * and according to each of the operations the new board will be updated. In addition, at the beginning we find
     * the empty place in the two-dimensional array, which will make it easier for us to update the board
     * @param action An action we want to run on the current board
     * @return The new state of the board after the operation is performed, that is, the updated
     * board after the operation
     */
    public State result(Action action) {
        this.board.updateString();
        String newBoardString = this.board.getBoardString();
        Board newBoard = new Board (newBoardString);
        int boardNumOfRows = newBoard.getBoardNumberOfRows();
        int boardNumOfCols = newBoard.getBoardNumberOfColumns();
        Direction direction = action.getDirection();
        int blankRowIdx = 0, blankColIdx = 0;
        for (int i = 0; i < boardNumOfRows; i++) {
            for (int j = 0; j < boardNumOfCols; j++) {
                int currentTileValue = newBoard.getTiles()[i][j].getValue();
                if (currentTileValue == 0) {
                    blankRowIdx = i;
                    blankColIdx = j;
                }
            }
        }
        if (direction == Direction.UP) {
            newBoard.getTiles()[blankRowIdx][blankColIdx] = newBoard.getTiles()[blankRowIdx + 1][blankColIdx];
            newBoard.getTiles()[blankRowIdx + 1][blankColIdx] = new Tile(0);
        }
        else if (direction == Direction.DOWN){
            newBoard.getTiles()[blankRowIdx][blankColIdx] = newBoard.getTiles()[blankRowIdx - 1][blankColIdx];
            newBoard.getTiles()[blankRowIdx - 1][blankColIdx] = new Tile(0);
        }
        else if (direction == Direction.RIGHT){
            newBoard.getTiles()[blankRowIdx][blankColIdx] = newBoard.getTiles()[blankRowIdx][blankColIdx - 1];
            newBoard.getTiles()[blankRowIdx][blankColIdx - 1] = new Tile(0);
        }
        else if (direction == Direction.LEFT){
            newBoard.getTiles()[blankRowIdx][blankColIdx] = newBoard.getTiles()[blankRowIdx][blankColIdx + 1];
            newBoard.getTiles()[blankRowIdx][blankColIdx + 1] = new Tile(0);
        }
        State newState = new State(newBoard);
        return newState;
    }

    public Board getBoard() {
        return board;
    }

    @Override
    public boolean equals(Object other) {
        if (!(other instanceof State)) {
            return false;
        }
        State otherState = (State) other;
        return board.equals(otherState.board);
    }

    @Override
    public int hashCode() {
        return board.hashCode();
    }
}