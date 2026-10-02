/**
 * The PathFromRoot class checks if a path exists from the root node of a binary tree to a given string.
 */
public class PathFromRoot {

    /**
     * Checks if a path exists from the root node to a given string.
     *
     * @param root the root node of the binary tree
     * @param str the string to check for a path
     * @return true if a path exists, false otherwise
     */
    public static boolean doesPathExist(BinNode<Character> root, String str) {
        int length = str.length();
        return doesPathExistt(root, str, length, 0);
    }

    /**
     * Helper method to recursively check if a path exists from a node to a given string.
     *
     * @param root the current node in the binary tree
     * @param str the string to check for a path
     * @param length the length of the string
     * @param index the current index in the string
     * @return true if a path exists, false otherwise
     */
    public static boolean doesPathExistt(BinNode<Character> root, String str, int length, int index) {
        if (length == index) {
            return true;
        }

        if (root == null) {
            return false;
        }

        if (str.charAt(index) == root.getData()) {
            return doesPathExistt(root.getLeft(), str, length, index+1) ||
                    doesPathExistt(root.getRight(), str, length, index+1);
        }

        return false;
    }
}
