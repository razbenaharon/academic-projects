public class StringBoard {

    /**
     *The function translates the string that displays the board into a two-dimensional array of type int
     * where each place represents a number according to the order in which it is represented in the string.
     * In fact, when passing through the string, each character of a number is inserted into a space in the array,
     * the character representing the space of the array advances by one index in order to receive the next number,
     * in the character '_' the number 0 will be inserted into the array, which represents that it is an empty space,
     * that is, an empty slot in our board . the character '|' Represents a row drop in the array because we have
     * finished receiving the number in the current row of the board.
     * @param boardString is the baord as the String displays it.
     * @return A two-dimensional array of type int that represents the board itself.
     */
    public static int[][] stringToArray(String boardString) {
        int rows = 1;
        for (int i = 0; i < boardString.length(); i++) {
            if (boardString.charAt(i) == '|') {
                rows++;
            }
        }
        int count1 = 0, index1 = 0, columns = 0, count2 = 0, index2 = 0;
        if (rows == 1) {
            while (count1 + index1 < boardString.length()) {
                if (boardString.charAt(count1 + index1) == ' ') {
                    columns++;
                    count1 += index1 + 1;
                    index1 = 0;
                }
                else if (boardString.charAt(count1 + index1) == '_') {
                    columns++;
                    count1 += 2;
                    index1 = 0;
                }
                else if (count1 + index1 == boardString.length() - 1) {
                    columns++;
                    count1 += index1 + 1;
                    index1 = 0;
                }
                else {
                    index1++;
                }
            }
        }
        else {
            while (boardString.charAt(count1) != '|') {
                if (boardString.charAt(count1 + index1) == ' ') {
                    columns++;
                    count1 += index1 + 1;
                    index1 = 0;
                }
                else if (boardString.charAt(count1 + index1) == '|') {
                    columns++;
                    count1 += index1;
                    index1 = 0;
                }
                else {
                    index1++;
                }
            }
        }
        int[][] boardArray = new int[rows][columns];
        int position1 = 0, position2 = 0;
        while (count2 + index2 <= boardString.length()) {
            if (position2 == columns) {
                position1++;
                position2 = 0;
            }
            if (count2 + index2 == boardString.length() || boardString.charAt(count2 + index2) == ' '
                    || boardString.charAt(count2 + index2) == '|' ) {
                int numberInBoard = Integer.parseInt(boardString.substring(count2, count2 + index2));
                boardArray[position1][position2] = numberInBoard;
                count2 += index2 + 1;
                index2 = 0;
                position2++;
            }
            else if (boardString.charAt(count2 + index2) == '_') {
                boardArray[position1][position2] = 0;
                count2 += index2 + 2;
                index2 = 0;
                position2++;
            }
            else {
                index2++;
            }
        }
        return boardArray;
    }

    /**
     * The function translates a two-dimensional array of type Tile to a string, so that the string can be
     * translated back to a two-dimensional array of type int and then to a two-dimensional array of type Tile to
     * complete the next movement in the array. In fact, we will insert into the string the first number with which
     * the array begins, and then and after each number inserted into it we will insert a space character.
     * Additionally, the number 0 will be represented in the string by '_' as it is an empty space in the array
     * (the empty space of the board is represented by the number 0 as no other number in the board can be 0 so we
     * can use this number). In addition, when we have finished going over any line in the array, we will add the
     * character '|'.
     * @param tiles A two-dimensional array of the Tile type where each cell represents a Tile ie a slot
     * @param boardNumberOfRows The number of rows in the two-dimensional array of type Tile
     * @param boardNumberOfColumns The number of columns in the two-dimensional array of type Tile
     * @return The function returns a string representing the new board in the same format as the strings of the
     * initial boards are written in the Main class
     */
    public static String tilesToString(Tile[][] tiles, int boardNumberOfRows, int boardNumberOfColumns) {
        String newBoardString = "";
        for (int i = 0; i < boardNumberOfRows; i++) {
            for (int j = 0; j < boardNumberOfColumns; j++) {
                if (tiles[i][j].getValue() == 0) {
                    newBoardString += '_';
                    if (j != boardNumberOfColumns - 1) {
                        newBoardString += ' ';
                    }
                }
                if (tiles[i][j].getValue() != 0) {
                    newBoardString += tiles[i][j].getValue();
                    if (j != boardNumberOfColumns - 1) {
                        newBoardString += ' ';
                    }
                }
                if (j == boardNumberOfColumns - 1) {
                    if (i != boardNumberOfRows - 1) {
                        newBoardString += '|';
                    }
                }
            }
        }
        return newBoardString;
    }
}