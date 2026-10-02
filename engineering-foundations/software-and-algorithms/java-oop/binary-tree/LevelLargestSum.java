import java.util.ArrayDeque;

public class LevelLargestSum {

    /**
     * Finds the level in a binary tree with the largest sum of node values.
     *
     * @param root the root node of the binary tree
     * @return the level with the largest sum, or -1 if the tree is empty
     */
    public static int getLevelWithLargestSum(BinNode<Integer> root) {
        if (root == null) {
            return -1;
        }

        ArrayDeque<BinNode<Integer>> queue = new ArrayDeque<>();
        queue.offer(root);
        int maxSum = Integer.MIN_VALUE;
        int levelWithMaxSum = 1;
        int currentLevel = 1;

        while (!queue.isEmpty()) {
            int num_of_elements = queue.size();
            int levelSum = 0;

            for (int i = 0; i < num_of_elements; i++) {
                BinNode<Integer> node = queue.poll();
                levelSum += node.getData();

                if (node.getLeft() != null) {
                    queue.offer(node.getLeft());
                }

                if (node.getRight() != null) {
                    queue.offer(node.getRight());
                }
            }

            if (levelSum > maxSum) {
                maxSum = levelSum;
                levelWithMaxSum = currentLevel;
            }

            currentLevel++;
        }

        return levelWithMaxSum;
    }
}
