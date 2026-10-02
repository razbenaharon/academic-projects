public class Negation extends Function {
    private Function function;
    public Negation(Function function) {
        this.function = function;
    }

    @Override
    public double valueAt(double x) {
        return -1 * function.valueAt(x);
    }

    @Override
    public String toString() {
        String negationString = "(" + "-" + function.toString() + ")";
        return negationString;
    }

    @Override
    public Negation derivative() {
        Function functionDerivative = function.derivative();
        return new Negation(functionDerivative);
    }

}
