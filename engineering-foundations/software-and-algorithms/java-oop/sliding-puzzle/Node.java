public class Node {
    private final Node parentNode;

    private final State state;

    private final Action preAction;

    public Node(State state) {
        /**
         constructor for the root node
         */
        this.state = state;
        this.parentNode = null;
        this.preAction = null;
    }

    public Node(State state, Action action, Node parentNode) {
        /**
         constructor for any node that is not root
         */
        this.state = state;
        this.parentNode = parentNode;
        this.preAction = action;
    }

    public Node[] expand() {
        /**
         An action called expand which expands the current root.
         operation does not accept parameters and returns an array of all
         nodes obtained from the extension.
         */
        Action[] actions = this.state.actions();
        int len = actions.length;
        Node[] expandedNode = new Node[len];
        for (int i = 0; i < len; i++) {
            Action currentAction = actions[i];
            expandedNode[i] = new Node(this.state.result(currentAction), currentAction, this);
        }
        return expandedNode;
    }

    public Node getParent() {
        return parentNode;
    }

    public State getState() {
        return state;
    }

    public Action getAction() {
        return preAction;
    }

    public int heuristicValue() {
        /**
         An action called heuristicValue, the operation does not accept parameters
         and returns the heuristicValue of the state that contained in the root.
         The heuristicValue calculate the sum of manhattan distance between the
         Tile in the board state board and the tile in the solution board (where it's supposed to be).
         */
        int heuristicValue = 0, solutionIndexOfRow, solutionIndexOfColumn, distanceInRow,
                distanceInColumn, manhattanDistance, currentNumber;
        for (int i = 0; i < state.getBoard().getBoardNumberOfRows(); i++) {
            for (int j = 0; j < state.getBoard().getBoardNumberOfColumns(); j++) {
                currentNumber = state.getBoard().getTiles()[i][j].getValue();
                if (currentNumber == 0) {
                    continue;
                }
                solutionIndexOfRow = state.getBoard().getSolutionTilesIndex()[0][currentNumber - 1];
                solutionIndexOfColumn = state.getBoard().getSolutionTilesIndex()[1][currentNumber - 1];
                distanceInRow = solutionIndexOfRow - i;
                distanceInColumn = solutionIndexOfColumn - j;
                distanceInRow = distanceInRow < 0 ? -distanceInRow : distanceInRow;
                distanceInColumn = distanceInColumn < 0 ? -distanceInColumn : distanceInColumn;
                manhattanDistance = distanceInRow + distanceInColumn;
                heuristicValue += manhattanDistance;
            }
        }
        return heuristicValue;
    }
}