import java.io.File;
import java.io.IOException;
import java.util.Random;
import java.util.Scanner;

public class Main {
    public static Scanner scanner;
    public static Random rnd;

    /**
     * digitsCalculator method receives a number 'i' and returns how many digits there are in the number.
     * It is used for printing the correct number of spaces before printing the number of the current row
     * when printing the board of the user or the cpu (computer).
     */
    public static int digitsCalculator(int i) {
        int counter = 0;
        if(i == 0) {
            return 1;
        }
        else {
            while(i > 0) {
                i = i / 10;
                counter++;
            }
        }
        return counter;
    }

    /**
     * printing a board of a player. First printing the numbers of columns and then each line starts with the
     * number of the current row with an amount of spaces and then the board itself.
     * @param board the board currently printed
     * @param numberOfRows: the number of rows each board has.
     * @param numberOfColumns: the number of columns each board has.
     * @param boardSizeRows: the number of rows each board has, as a string, used for extracting its length to
     *                     an int and printing the correct number of spaces after printing the current column.
     *                     For example, after printing the column number "12" we need to print a space after the
     *                     "-" char so there will be correlation between the "-" char and the column number.
     */

    public static void boardPrinter(char[][] board, int numberOfRows, int numberOfColumns, String boardSizeRows,
                                    String boardSizeColumns) {
        int numberOfRowsStringLength = boardSizeRows.length();
        int numberOfColumnsStringLength = boardSizeColumns.length();
        for(int i = -1; i < numberOfColumns; i++) {
            if(i == -1) {
                for(int j = 0; j < numberOfRowsStringLength; j++) {
                    System.out.print(" ");
                }
            }
            else {
                System.out.print(" " + i);
            }
        }
        System.out.print("\n");
        for(int i = 0; i < numberOfRows; i++) {
            for(int j = -1; j < numberOfColumns; j++) {
                if(j == -1) {
                    int numberOfDigits = digitsCalculator(i);
                    int numberOfSpaces = numberOfRowsStringLength - numberOfDigits;
                    for(int k = 0; k < numberOfSpaces; k++) {
                        System.out.print(" ");
                    }
                    System.out.print(i);
                }
                else {
                    System.out.print(" " + board[i][j]);
                    int extraSpaces = digitsCalculator(j) - 1;
                    for(int k = 0; k < extraSpaces; k++) {
                        System.out.print(" ");
                    }
                }
            }
            System.out.print("\n");
        }
        System.out.print("\n");
    }

    /**
     * recevies the orientation of the current submarine that is placed and checks if the value of orientation
     * is 0 or 1, which are the only two options legal for a submarine.
     */
    public static boolean legalOrientation(int orientation) {
        if(orientation == 0 || orientation == 1){
            return true;
        }
        else{
            return false;
        }
    }

    /**
     * Checks if the coordination entered is inside the board's bounds.
     * @param numberOfRows: the number of rows each board has.
     * @param numberOfColumns: the number of columns each board has.
     * @param x: the x coordination in the string of the submarine attributes.
     * @param y the y coordination in the string of the submarine attributes.
     */

    public static boolean legalCoordinationInBounds(int numberOfRows, int numberOfColumns, int x, int y) {
        if(x >= 0 && x < numberOfRows && y >= 0 && y < numberOfColumns) {
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * Checks if a submarine is in bounds. Done by checking if each coordinate is in bounds (the other parameters
     * explained in the functions above).
     * @return
     */

    public static boolean legalSubmarineInBounds(char[][] board, int numberOfRows, int numberOfColumns, int x, int y,
                                                 int orientation, int sizeOfSubmarines) {
        if(orientation == 0) {
            for(int i = 0; i < sizeOfSubmarines; i++) {
                if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x, y + i) == false) {
                    return false;
                }
            }
            return true;
        }
        else if(orientation == 1) {
            for(int i = 0; i < sizeOfSubmarines; i++) {
                if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + i, y) == false) {
                    return false;
                }
            }
            return true;
        }
        return true;
    }

    /**
     * Checks if there is no already a submarine in the coordinations in which the current submarine
     * supposed to be (the other parameters
     *      * explained in the functions above).
     */

    public static boolean legalNotClash(char[][] board, int numberOfRows, int numberOfColumns, int x, int y,
                                        int orientation, int sizeOfSubmarines) {
        if(orientation == 0) {
            for(int i = 0; i < sizeOfSubmarines; i++) {
                if(board[x][y+i] == '#') {
                    return false;
                }
            }
            return true;
        }
        else if(orientation == 1) {
            for(int i = 0; i < sizeOfSubmarines; i++) {
                if(board[x+i][y] == '#') {
                    return false;
                }
            }
            return true;
        }
        return true;
    }

    /**
     *
     * Checks if the current submarine placed does not penetrate to the field around other submarines, in
     * case the current submarine has a size of only one square. Done by checking if the field around
     * the current submarine is clean and has no other submarines (the other parameters
     *      * explained in the functions above).
     */

    public static boolean legalNotPenetrateSizeOfOne(char[][] board, int numberOfRows, int numberOfColumns, int x,
                                                     int y, int sizeOfSubmarines) {
        for(int i = x - 1; i <= x + 1; i++) {
            for(int j = y - 1; j <= y + 1; j++) {
                if(i == x && j == y) {
                    continue;
                }
                else {
                    if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, j) == false) {
                        continue;
                    }
                    else {
                        if(board[i][j] == '#') {
                            return false;
                        }
                    }
                }
            }
        }
        return true;
    }

    /**
     * Checks if the current submarine placed does not penetrate to the field around other submarines, in
     *      * case the current submarine is horizontal and has a size larger than one square
     *      Done by checking if the field around the current submarine is clean and has no other submarines.
     *      the body of the submarine and it's edges are checked separately.
     *      (the other parameters
     *      explained in the functions above).
     */

    public static boolean legalNotPenetrateHorizontalSizeMoreThanOne(char[][] board, int numberOfRows,
                                                                     int numberOfColumns, int x, int y,
                                                                     int sizeOfSubmarines) {
        for(int i = y; i <= y + sizeOfSubmarines - 1; i++) {
            if(i == y) {
                for(int j = 0; j < 5; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + 1, i) == true) {
                            if(board[x + 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x - 1, i) == true) {
                            if(board[x - 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 2) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x, i - 1) == true) {
                            if(board[x][i - 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 3) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + 1, i - 1) == true) {
                            if(board[x + 1][i - 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 4) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x - 1, i - 1) == true) {
                            if(board[x - 1][i - 1] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
            else if(i == y + sizeOfSubmarines - 1) {
                for(int j = 0; j < 5; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + 1, i) == true) {
                            if(board[x + 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1){
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x - 1, i) == true) {
                            if(board[x - 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 2){
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + 1, i + 1) == true) {
                            if(board[x + 1][i + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 3){
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x, i + 1) == true) {
                            if(board[x][i + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 4) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x - 1, i + 1) == true) {
                            if(board[x - 1][i + 1] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
            else {
                for(int j = 0; j < 2; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x + 1, i) == true) {
                            if(board[x + 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x - 1, i) == true) {
                            if(board[x - 1][i] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
        }
        return true;
    }

    /**
     *
     Checks if the current submarine placed does not penetrate to the field around other submarines, in
     *      * case the current submarine is vertical and has a size larger than one square.
     *      Done by checking if the field around the current submarine is clean and has no other submarines.
     *      the body of the submarine and it's edges are checked separately.
     *      (the other parameters
     *      explained in the functions above).
     */

    public static boolean legalNotPenetrateVerticalSizeMoreThanOne(char[][] board, int numberOfRows,
                                                                   int numberOfColumns, int x, int y,
                                                                   int sizeOfSubmarines) {
        for(int i = x; i <= x + sizeOfSubmarines - 1; i++) {
            if(i == x) {
                for(int j = 0; j < 5; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y + 1) == true) {
                            if(board[i][y + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y - 1) == true) {
                            if(board[i][y - 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 2) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i - 1, y) == true) {
                            if(board[i - 1][y] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 3) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i - 1, y + 1) == true) {
                            if(board[i - 1][y + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 4) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i - 1, y - 1) == true) {
                            if(board[i - 1][y - 1] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
            else if(i == x + sizeOfSubmarines - 1) {
                for(int j = 0; j < 5; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y + 1) == true) {
                            if(board[i][y + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y - 1) == true) {
                            if(board[i][y - 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 2) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i + 1, y + 1) == true) {
                            if(board[i + 1][y + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 3) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i + 1, y) == true) {
                            if(board[i + 1][y] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 4) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i + 1, y - 1) == true) {
                            if(board[i + 1][y - 1] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
            else {
                for(int j = 0; j < 2; j++) {
                    if(j == 0) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y + 1) == true) {
                            if(board[i][y + 1] == '#') {
                                return false;
                            }
                        }
                    }
                    else if(j == 1) {
                        if(legalCoordinationInBounds(numberOfRows, numberOfColumns, i, y - 1) == true) {
                            if(board[i][y - 1] == '#') {
                                return false;
                            }
                        }
                    }
                }
            }
        }
        return true;
    }

    /**
     Checks if the current submarine placed does not penetrate to the field around other submarines,
     *      Done by checking if the field around the current submarine is clean and has no other submarines.
     *      We separate to different cases, in which the submarine has a size of only one square,
     *      or if it's larger than one and horizontal, or it's larger than one and vertical.
     *      (the other parameters
     *      explained in the functions above).
     */

    public static boolean legalNotPenetrate(char[][] board, int numberOfRows, int numberOfColumns, int x, int y,
                                            int orientation, int sizeOfSubmarines) {
        if(orientation == 0) {
            if(sizeOfSubmarines == 1) {
                boolean sign1 = legalNotPenetrateSizeOfOne(board, numberOfRows, numberOfColumns,
                        x, y, sizeOfSubmarines);
                if(sign1 == false) {
                    return false;
                }
                else {
                    return true;
                }
            }
            else {
                boolean sign2 = legalNotPenetrateHorizontalSizeMoreThanOne(board, numberOfRows, numberOfColumns,
                        x, y, sizeOfSubmarines);
                if(sign2 == false) {
                    return false;
                }
                else {
                    return true;
                }
            }
        }
        else if(orientation == 1) {
            if(sizeOfSubmarines == 1) {
                boolean sign3 = legalNotPenetrateSizeOfOne(board, numberOfRows, numberOfColumns,
                        x, y, sizeOfSubmarines);
                if(sign3 == false) {
                    return false;
                }
                else {
                    return true;
                }
            }
            else {
                boolean sign4 = legalNotPenetrateVerticalSizeMoreThanOne(board, numberOfRows, numberOfColumns,
                        x, y, sizeOfSubmarines);
                if(sign4 == false) {
                    return false;
                }
                else {
                    return true;
                }
            }
        }
        return true;
    }

    /**
     Places the submarine according to the orientation and size of the submarine (the parameters
     that the function receives are explained above).
     */

    public static void placing(char[][] board, int numberOfRows, int numberOfColumns, int x, int y,
                               int orientation, int sizeOfSubmarines) {
        if(orientation == 0) {
            for(int i = y; i <= y + sizeOfSubmarines - 1; i++) {
                board[x][i] = '#';
            }
        }
        else if(orientation == 1) {
            for(int i = x; i <= x + sizeOfSubmarines - 1; i++) {
                board[i][y] = '#';
            }
        }
    }

    /**
     Checks if the submarine is legal to be placed. It checks if the orientation of the submarine is legal,
     if it's coordinations are in the board (first checking it's first coordination), if it does not
     clash with other submarine already in the board, and if it does not penetrate the field around other
     submarine already in the board. the Checking is done in the order as explained and printing an error
     message for as the first testing fails. If all tests return true (legal) than the submarine is placed.
     (the parameters
     that the function receives are explained above).
     */
    public static int isLegalPlusPlacing(char[][] board, int numberOfRows, int numberOfColumns, int x,
                                         int y, int orientation , int sizeOfSubmarines) {
        for(int i = 0; i < 6; i++) {
            if(i == 0) {
                if(legalOrientation(orientation) == false) {
                    System.out.println("Illegal orientation, try again!");
                    return 0;
                }
            }
            else if(i == 1) {
                if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x, y) == false) {
                    System.out.println("Illegal tile, try again!");
                    return 0;
                }
            }
            else if(i == 2) {
                if(legalSubmarineInBounds(board, numberOfRows, numberOfColumns, x, y, orientation,
                        sizeOfSubmarines) == false) {
                    System.out.println("Battleship exceeds the boundaries of the board, try again!");
                    return 0;
                }
            }
            else if(i == 3) {
                if(legalNotClash(board, numberOfRows, numberOfColumns, x, y, orientation, sizeOfSubmarines) == false) {
                    System.out.println("Battleship overlaps another battleship, try again!");
                    return 0;
                }
            }
            else if(i == 4) {
                if(legalNotPenetrate(board, numberOfRows, numberOfColumns, x, y, orientation,
                        sizeOfSubmarines) == false) {
                    System.out.println("Adjacent battleship detected, try again!");
                    return 0;
                }
            }
            else if(i == 5) {
                placing(board, numberOfRows, numberOfColumns, x, y, orientation, sizeOfSubmarines);
            }
        }
        return 1;
    }

    /**
     Handles the cpu board.
     Checks if the submarine is legal to be placed. It checks if the orientation of the submarine is legal,
     if it's coordinations are in the board (first checking it's first coordination), if it does not
     clash with other submarine already in the board, and if it does not penetrate the field around other
     submarine already in the board. the Checking is done in the order as explained and printing an error
     message for as the first testing fails. If all tests return true (legal) than the submarine is placed.
     (the parameters
     that the function receives are explained above).
     */

    public static int isLegalPlusPlacingCpu(char[][] board, int numberOfRows, int numberOfColumns, int x, int y,
                                            int orientation,
                                            int sizeOfSubmarines) {
        for(int i = 0; i < 6; i++) {
            if(i == 0) {
                if(legalOrientation(orientation) == false) {
                    return 0;
                }
            }
            else if(i == 1) {
                if(legalCoordinationInBounds(numberOfRows, numberOfColumns, x, y) == false) {
                    return 0;
                }
            }
            else if(i == 2) {
                if(legalSubmarineInBounds(board, numberOfRows, numberOfColumns, x, y, orientation,
                        sizeOfSubmarines) == false) {
                    return 0;
                }
            }
            else if(i == 3) {
                if(legalNotClash(board, numberOfRows, numberOfColumns, x, y, orientation,
                        sizeOfSubmarines) == false) {
                    return 0;
                }
            }
            else if(i == 4) {
                if(legalNotPenetrate(board, numberOfRows, numberOfColumns, x, y, orientation,
                        sizeOfSubmarines) == false) {
                    return 0;
                }
            }
            else if(i == 5) {
                placing(board, numberOfRows, numberOfColumns, x, y, orientation, sizeOfSubmarines);
            }
        }
        return 1;
    }

    /**
     * Extract the attributes of the submarine from it's string (aboutSubmarine string) to x, y, and orientation
     * into ints so we can pass them to different functions and use them for legal checking and other methods.
     * @param userBoard the board of the user.
     * @param numberOfRows the number of rows each board contains.
     * @param numberOfColumns the number of columns each board contains.
     * @param aboutSubmarine the string that contains the submarine's coordination and orientation.
     * @param sizeOfSubmarines sizeOfSubmrines varibale is the size of the current submrine being placed, because we place the
     *      *      submarines from the smallest to the largest and place different number of submarines for every size
     *      *      entered to the string.
     * @return
     */



    public static int aboutSubmarineToInt(char[][] userBoard, int numberOfRows, int numberOfColumns,
                                          String aboutSubmarine,
                                          int sizeOfSubmarines) {
        int index=0, count1=0, count2=0, count3=0;
        while(1 == 1) {
            if(aboutSubmarine.charAt(index + count1) == ',') {
                break;
            }
            else {
                count1++;
            }
        }
        int x = Integer.parseInt(aboutSubmarine.substring(index, index + count1));
        index += count1 + 2;
        while(1 == 1) {
            if(aboutSubmarine.charAt(index + count2) == ',') {
                break;
            }
            else {
                count2++;
            }
        }
        int y = Integer.parseInt(aboutSubmarine.substring(index, index + count2));
        index += count2 + 2;
        while(1 == 1) {
            if(index + count3 == aboutSubmarine.length()) {
                break;
            }
            else {
                count3++;
            }
        }
        int orientation = Integer.parseInt(aboutSubmarine.substring(index, index + count3));
        return isLegalPlusPlacing(userBoard, numberOfRows, numberOfColumns, x, y, orientation, sizeOfSubmarines);
    }


    /**
     * Generates random cordintaes (x, y, and oriention) and check if it is legal (all the condtion of placing a submarine are ture)
     * Then its updating the submarine board with the new submarine and finish the loop
     * @param cpuBoard the board of the cpu - used for the legal check.
     * @param numberOfRows the number of rows each board contains.
     * @param numberOfColumns the number of columns each board contains.
     * @param submarineBoardCpu a 2D array containing the coordinates of each submarine placed by the CPU.
     * @param currentSubmarineTotal used for a counter of the current submarine that is placed
     * @param sizeOfSubmarines sizeOfSubmrines varibale is the size of the current submarine being placed, because we place the
     *      *      submarines from the smallest to the largest and place different number of submarines for every size
     *      *      entered to the string.
     * @return
     */
    public static void cpuSubmarinePlacer(char[][] cpuBoard, int numberOfRows, int numberOfColumns,
                                          int sizeOfSubmarines,
                                          String[][] submarineBoardCpu,
                                          int currentSubmarineTotal) {
        int flagOfDone = 0, cpuX, cpuY, cpuOrientation;
        while(flagOfDone == 0) {
            cpuX = rnd.nextInt(numberOfRows);
            cpuY = rnd.nextInt(numberOfColumns);
            cpuOrientation = rnd.nextInt(2);
            String aboutSubmarine = (cpuX + ", " + cpuY + ", " + cpuOrientation);
            if(isLegalPlusPlacingCpu(cpuBoard, numberOfRows, numberOfColumns, cpuX, cpuY,
                    cpuOrientation, sizeOfSubmarines) == 1) {
                updateSubmarineBoard(submarineBoardCpu, aboutSubmarine, sizeOfSubmarines, currentSubmarineTotal);
                flagOfDone = 1;
            }
        }
    }

    /**
        converts the string of the submarine numeber and sizes (for example : 1X3 4X5 6X7)
        to an array of ints on the same order without the X
        for the example above: [1,3,4,5,6,7]
        and than returning the array
     */
    public static int[] stringToBoard(String submarines) {
        int numOfSubmarine = (submarines.length() + 1) / 4;
        int[] submarine = new int[(submarines.length() + 1) / 2];
        int number = 0, size = 0, newStartIndex = 0;
        for(int i = 0; i < numOfSubmarine * 2; i += 2) {
            int[] submarineNumSize = stringSizeToInt(submarines, 'X', newStartIndex);
            number = submarineNumSize[0];
            size = submarineNumSize[1];
            newStartIndex = submarineNumSize[2];
            submarine[i] = number;
            submarine[i + 1] = size;
        }
        return submarine;
    }

    /**
     * the submarine board is a 2D array containing the coordinates of each submarine placed by the CPU/USER
     * this func is placing the coordinate of one sumbarine each time in the 2D arr
     * @param sizeOfSubmarine the number of coordiantes we need to update is the size of the sumbarine
     * @param numOfSubmarine the cuurent num of the submarine we place - row of the board
     * @param aboutSubmarine the string that contains the submarine's coordination and orientation.
     * @param submarineBoard a 2D array containing the coordinates of each submarine placed by the CPU/User
     * @return
     */
    public static void updateSubmarineBoard(String[][] submarineBoard, String aboutSubmarine, int sizeOfSubmarine,
                                            int numOfSubmarine) {
        int coordination[] = stringSizeToInt(aboutSubmarine, ',', 0);
        int x = coordination[0];
        int y = coordination[1];
        int index = coordination[2];
        int orientation[] = stringSizeToInt(aboutSubmarine, ',', index - 2);
        int orientationValue = orientation[1];
        for(int j = 0; j < sizeOfSubmarine; j++) {
            if(orientationValue == 1) {
                String cordinataOne = (Integer.toString(x + j) + ',' + ' ' + Integer.toString(y));
                submarineBoard[numOfSubmarine][j] = cordinataOne;
            }
            if(orientationValue == 0) {
                String cordinataZero = (Integer.toString(x) + ',' + ' ' + Integer.toString(y + j));
                submarineBoard[numOfSubmarine][j] = cordinataZero;
            }
        }
    }

    /**
     * this function is reading the submarine numeber and sizes (for example : 1X3 4X5 6X7)
     * and then reading cordaintes from the user and if it is legal - placing the submarine and updating the new cordinates in the submarineBoard
     * @param  boardSizeRows is used only for the board printer
     * @param  numberOfColumns is used only for the board printer
     * @param submarineBoardUser a 2D array containing the coordinates of each submarine placed by the User
     * @param submarineBoardCpu a 2D array containing the coordinates of each submarine placed by the CPU
     * @param userBoard the board of the user.
     * @param numberOfRows the number of rows each board contains.
     * @param numberOfColumns the number of columns each board contains.
     * @param cpuBoard the board of the cpu.
     * @param submarines string of the submarine numeber and sizes (for example : 1X3 4X5 6X7)
     * @return
     */
    public static void placingSubmarines(char[][] userBoard, char[][] cpuBoard, int numberOfRows,
                                         int numberOfColumns, String submarines,
                                         String boardSizeRows, String boardSizeColumns,
                                         String[][] submarineBoardUser, String[][] submarineBoardCpu) {
        int[] submarine = new int[(submarines.length() + 1) / 2];
        int numOfSubmarine = (submarines.length() + 1) / 4;
        int currentSubmarine, numOfSubmarines, sizeOfSubmarines;
        int newStartIdx = 0, currentSubmarineTotal = 0;
        for(int i = 0; i < numOfSubmarine * 2; i += 2) {
            currentSubmarine = 0;
            int[] submarineNumSize = stringSizeToInt(submarines, 'X' , newStartIdx);
            numOfSubmarines = submarineNumSize[0];
            sizeOfSubmarines = submarineNumSize[1];
            newStartIdx = submarineNumSize[2];
            submarine[i] = numOfSubmarines;
            submarine[i + 1] = sizeOfSubmarines;
            System.out.println("Enter location and orientation for battleship of size " + sizeOfSubmarines);
            while(currentSubmarine < numOfSubmarines) {
                String submarineCord = scanner.nextLine();
                int result = aboutSubmarineToInt(userBoard, numberOfRows, numberOfColumns, submarineCord,
                        sizeOfSubmarines);
                if(result == 1) {
                    updateSubmarineBoard(submarineBoardUser, submarineCord, sizeOfSubmarines, currentSubmarineTotal);
                    System.out.println("Your current game board:");
                    boardPrinter(userBoard, numberOfRows, numberOfColumns, boardSizeRows, boardSizeColumns);
                    cpuSubmarinePlacer(cpuBoard, numberOfRows, numberOfColumns, sizeOfSubmarines,
                             submarineBoardCpu, currentSubmarineTotal);
                    currentSubmarine++;
                    currentSubmarineTotal++;
                    if(currentSubmarine != numOfSubmarines) System.out.println("Enter location and orientation for " +
                            "battleship" +
                            " of size " + sizeOfSubmarines);
                }
            }
        }
    }

    /**
     * this function is getiing a string (for example : 1X3 4X5 6X7) or (for example : (0, 3))
     * and then placing in a arr of ints in size of 3 :
     * number[0] - rescue the first number from the start index
     * number[1] - rescue the first number after the char
     * number[2] - the index of the second number - (if we call the func once again)
     * @param  char1 the buffer between the numbers
     * @param  start start index
     * @param  str the string we need to get the number from
     * @return
     */

    public static int[] stringSizeToInt(String str, char char1, int start) {
        int index = 0;
        int[] number = {0, 0, 0};
        while(str.charAt(start + index) != char1) {
            index++;
        }
        number[0] = Integer.parseInt(str.substring(start, start + index));
        if(char1 == ',')
            index++;
        start += index + 1;
        index = 0;
        while(start + index < str.length()) {
            if(str.charAt(start + index) == ' ' || str.charAt(start + index) == char1){
                break;
            }
            index++;
        }
        number[1] = Integer.parseInt(str.substring(start, start + index));
        number[2]= start + index + 1;
        return number;
    }

    /**
     * resets the submarineBoard to a "-" string in every cell. it will be used to determine if a submarine has drawned
     * @param submarineBoard a 2D array containing the coordinates of each submarine placed by the CPU/USER
     * @return
     */
    public static void resetBoard(char[][] submarineBoard, int numberOfRows, int numberOfColumns) {
        for(int i = 0; i < numberOfRows; i++) {
            for(int j = 0; j < numberOfColumns; j++) {
                submarineBoard[i][j] = '–';
            }
        }
    }

    /**
     * creates the submarine board with the total num of submarines as a row and the biggest size of submarine as a column
     * @param submarine string contains submarine number and sizes (for example : 1X3 4X5 6X7)
     * @param size size of submarine arr
     * @return
     */

    public static String[][] submarineBoardCreator(int[] submarine, int size) {
        int totalSubmarine = 0;
        int biggestSubmarine = submarine[1];
        int temp = 0;
        for(int i = 0; i < size; i += 2) {
            totalSubmarine += submarine[i];
        }
        for(int i = 1; i < size; i += 2) {
            temp = submarine[i];
            if(temp > biggestSubmarine) {
                biggestSubmarine = temp;
            }
        }
        String[][] submarineBoard = new String[totalSubmarine][biggestSubmarine];
        for(int i = 0; i < totalSubmarine; i++) {
            for(int j = 0; j < biggestSubmarine; j++) {
                submarineBoard[i][j] = "-" ;
            }
        }
        return submarineBoard;
    }
    /**
     * returns the biggest size of submarine
     * @param submarine string contains submarine number and sizes (for example : 1X3 4X5 6X7)
     * @param size size of submarine arr
     * @return
     */
    public static int submarineBoardCol(int[] submarine, int size) {
        int biggestSubmarine = submarine[1];
        int temp = 0;
        for(int i = 1; i < size; i += 2) {
            temp = submarine[i];
            if(temp > biggestSubmarine){
                biggestSubmarine=temp;
            }
        }
        return biggestSubmarine;
    }

    /**
     * returns the total num of submarines
     * @param submarine string contains submarine number and sizes (for example : 1X3 4X5 6X7)
     * @param size size of submarine arr
     * @return
     */
    public static int submarineBoardRow(int[] submarine, int size) {
        int totalSubmarine = 0;
        int biggestSubmarine = submarine[1];
        for(int i = 0; i < size; i += 2) {
            totalSubmarine += submarine[i];
        }
        return totalSubmarine;
    }

    /**
     * returns the num of submarine alive (the number of cols fill with "-") in submarineBoard
     * @param submarineBoard a 2D array containing the coordinates of each submarine placed by the CPU/USER
     * @return
     */
    public static int checkNumOfSubmarineAlive(String[][] submarineBoard, int numberOfRows, int numberOfColumns) {
        int alive = 0;
        for(int i = 0; i < numberOfRows; i++) {
            for(int j = 0; j < numberOfColumns; j++) {
                if(!(submarineBoard[i][j].equals("-"))) {
                    alive++;
                    break;
                }
            }
        }
        return alive;
    }
    /**
     * this function responsable for the attack of the ships - of the user and cpu
     * I will explain on the user attack - the same checks is with the cpu the only differnt is that the user need to enter cordinate
     * and the cpu is generating random one
     *  first getting the cordainates from the user check in the gusessing board if the coordinate already attacked- if yes start over get new cordinate
     *  then check on the submarine board if the cordinate is an enemys submarine
     *  if it is its check if the num of submarine has been changed
     *  and then check if the num is 0 it means al the submarines drawned and the game is over
     *  if it is not an enemys ship is markes as a miss
     * @param  boardSizeRows is used only for the board printer
     * @param  numberOfColumns is used only for the board printer
     * @param submarineBoardUser a 2D array containing the coordinates of each submarine placed by the User
     * @param submarineBoardCpu a 2D array containing the coordinates of each submarine placed by the CPU
     * @param userBoard the board of the user.
     * @param numberOfRows the number of rows each board contains.
     * @param numberOfColumns the number of columns each board contains.
     * @param cpuBoard the board of the cpu.
     * @param submarines string of the submarine numeber and sizes (for example : 1X3 4X5 6X7)
     * @return
     */
    public static void attackSubmarines(char[][] userGuessingBoard, char[][] cpuGuessingBoard, char[][] userBoard,
                                        char[][] cpuBoard, int numberOfRows, int numberOfColumns, String boardSizeRows,
                                        String boardSizeColumns, String submarines, String[][] submarineBoardUser,
                                        int submarineBoardRow, int submarineBoardColumn,
                                        String[][] submarineBoardCpu) {
        int numberOfSubmarineAliveCpu = checkNumOfSubmarineAlive(submarineBoardCpu, submarineBoardRow,
                submarineBoardColumn);
        int numberOfSubmarineAliveUser = checkNumOfSubmarineAlive(submarineBoardCpu, submarineBoardRow,
                submarineBoardColumn);
        int repeat = 0;
        System.out.println("Your current guessing board:");
        boardPrinter(userGuessingBoard, numberOfRows, numberOfColumns, boardSizeRows, boardSizeColumns);
        while(1 == 1) {
            if(repeat == 0) System.out.println("Enter a tile to attack");
            String cordination = scanner.nextLine();
            int[] xy = stringSizeToInt(cordination, ',', 0);
            int x = xy[0];
            int y = xy[1];
            if(x < 0 || x >= numberOfRows || y < 0 || y >= numberOfColumns) {
                System.out.println("Illegal tile, try again!");
                repeat = 1;
                continue;
            }
            if(userGuessingBoard[x][y] != '–') {
                System.out.println("Tile already attacked, try again!");
                repeat = 1;
                continue;
            }
            for(int i = 0; i < submarineBoardRow; i++) {
                for(int j = 0; j < submarineBoardColumn; j++) {
                    if(cordination.equals(submarineBoardCpu[i][j])) {
                        System.out.println("That is a hit!");
                        submarineBoardCpu[i][j] = "-";
                        cpuBoard[x][y] = 'X';
                        userGuessingBoard[x][y] = 'V';
                        checkNumOfSubmarineAlive(submarineBoardCpu, submarineBoardRow, submarineBoardColumn);
                        if(numberOfSubmarineAliveCpu != checkNumOfSubmarineAlive(submarineBoardCpu,
                                submarineBoardRow, submarineBoardColumn)) {
                            numberOfSubmarineAliveCpu = checkNumOfSubmarineAlive(submarineBoardCpu,
                                    submarineBoardRow, submarineBoardColumn);
                            System.out.println("The computer's battleship has been drowned, " +
                                    numberOfSubmarineAliveCpu + " more battleships to go!");
                            if(numberOfSubmarineAliveCpu == 0) {
                                System.out.println("You won the game!");
                                return;
                            }
                        }
                    }
                }
            }
            if(cpuBoard[x][y] == '–') {
                System.out.println("That is a miss!");
                userGuessingBoard[x][y] = 'X';
            }
            repeat = 0;
            while(1 == 1) {
                int cpuX = rnd.nextInt(numberOfRows);
                int cpuY = rnd.nextInt(numberOfColumns);
                String cordinationCpu = (cpuX + ", " + cpuY);
                if(cpuGuessingBoard[cpuX][cpuY] != '–') {
                    continue;
                }
                System.out.println("The computer attacked (" + cordinationCpu + ")");
                for(int i = 0; i < submarineBoardRow; i++) {
                    for(int j = 0; j < submarineBoardColumn; j++) {
                        if(cordinationCpu.equals(submarineBoardUser[i][j])) {
                            System.out.println("That is a hit!");
                            submarineBoardUser[i][j] = "-";
                            userBoard[cpuX][cpuY] = 'X';
                            cpuGuessingBoard[cpuX][cpuY] = 'V';
                            if(numberOfSubmarineAliveUser != checkNumOfSubmarineAlive(submarineBoardUser,
                                    submarineBoardRow, submarineBoardColumn)) {
                                numberOfSubmarineAliveUser = checkNumOfSubmarineAlive(submarineBoardUser,
                                        submarineBoardRow, submarineBoardColumn);
                                System.out.println("Your battleship has been drowned, you have left " +
                                        numberOfSubmarineAliveUser + " more battleships!");
                                if(numberOfSubmarineAliveUser == 0) {
                                    System.out.println("Your current game board:");
                                    boardPrinter(userBoard, numberOfRows, numberOfColumns, boardSizeRows,
                                            boardSizeColumns);
                                    System.out.println("You lost ):");
                                    return;
                                }
                            }
                        }
                    }
                }
                if(userBoard[cpuX][cpuY] == '–') {
                    System.out.println("That is a miss!");
                    cpuGuessingBoard[cpuX][cpuY] = 'X';
                }
                System.out.println("Your current game board:");
                boardPrinter(userBoard, numberOfRows, numberOfColumns, boardSizeRows, boardSizeColumns);
                System.out.println("Your current guessing board:");
                boardPrinter(userGuessingBoard, numberOfRows, numberOfColumns, boardSizeRows, boardSizeColumns);
                break;
            }
        }
    }
    /**
     the functions that manage the game- creates the necessary boards, strings and variables reset them and arrays and call the the functions mansions above     * @return
     */
    public static void battleshipGame() {
        System.out.println("Enter the board size");
        String boardSize = scanner.nextLine();
        int[] amountOfRowsAndColumns = stringSizeToInt(boardSize, 'X', 0);
        int numberOfRows = amountOfRowsAndColumns[0];
        int numberOfColumns = amountOfRowsAndColumns[1];
        String boardSizeRows = Integer.toString(numberOfRows);
        String boardSizeColumns = Integer.toString(numberOfColumns);
        char[][] userBoard = new char[numberOfRows][numberOfColumns];
        char[][] cpuBoard = new char[numberOfRows][numberOfColumns];
        char[][] userGuessingBoard = new char[numberOfRows][numberOfColumns];
        char[][] cpuGuessingBoard = new char[numberOfRows][numberOfColumns];
        resetBoard(userBoard, numberOfRows, numberOfColumns);
        resetBoard(cpuBoard, numberOfRows, numberOfColumns);
        resetBoard(userGuessingBoard, numberOfRows, numberOfColumns);
        resetBoard(cpuGuessingBoard, numberOfRows, numberOfColumns);
        System.out.println("Enter the battleships sizes");
        String submarinesAmountsAndSizes = scanner.nextLine();
        System.out.println("Your current game board:");
        int[] submarineStr = stringToBoard(submarinesAmountsAndSizes);
        String[][] submarineBoardUser = submarineBoardCreator(submarineStr,
                (submarinesAmountsAndSizes.length() + 1) / 2);
        String[][] submarineBoardCpu = submarineBoardCreator(submarineStr,
                (submarinesAmountsAndSizes.length() + 1) / 2);
        int submarineBoardRow = submarineBoardRow(submarineStr, (submarinesAmountsAndSizes.length() + 1) / 2);
        int submarineBoardColumn = submarineBoardCol(submarineStr, (submarinesAmountsAndSizes.length() + 1) / 2);
        boardPrinter(userBoard, numberOfRows, numberOfColumns, boardSizeRows, boardSizeColumns);
        placingSubmarines(userBoard, cpuBoard, numberOfRows, numberOfColumns, submarinesAmountsAndSizes, boardSizeRows,
                boardSizeColumns,
                submarineBoardUser, submarineBoardCpu);
        attackSubmarines(userGuessingBoard, cpuGuessingBoard, userBoard, cpuBoard, numberOfRows, numberOfColumns,
                boardSizeRows,
                boardSizeColumns, submarinesAmountsAndSizes, submarineBoardUser, submarineBoardRow,
                submarineBoardColumn, submarineBoardCpu);
    }
    /**
     the  main function only get the number of games, the current random seed
     and then call the batllship game function number of games times
     */
    public static void main(String[] args) throws IOException {
        String path = args[0];
        scanner = new Scanner(new File(path));
        int numberOfGames = scanner.nextInt();
        scanner.nextLine();
        System.out.println("Total of " + numberOfGames + " games.");
        for (int i = 1; i <= numberOfGames; i++) {
            scanner.nextLine();
            int seed = scanner.nextInt();
            rnd = new Random(seed);
            scanner.nextLine();
            System.out.println("Game number " + i + " starts.");
            battleshipGame();
            System.out.println("Game number " + i + " is over.");
            System.out.println("------------------------------------------------------------");
        }
        System.out.println("All games are over.");
    }
}