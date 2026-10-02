public class Constant extends Polynomial {
    private double constant;

    public Constant(double constant) {
        this.constant = constant;
    }

    @Override
    public double valueAt(double x) {
        return constant;
    }

    @Override
    public String toString() {
        String constantString;
        if (constant % 1 == 0) {
            constantString = "(" + String.format("%.0f", constant) + ")";
        }
        else {
            constantString = "(" + constant + ")";
        }
        return constantString;
    }
    @Override
    public Constant derivative() {
        /**
        *const derivative is always 0
         */
        return new Constant(0);
    }
}