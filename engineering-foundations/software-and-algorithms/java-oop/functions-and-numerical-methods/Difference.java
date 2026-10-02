public class Difference extends Function {
    private Function[] functions;

    public Difference(Function... functions) {
        this.functions = functions;
    }

    @Override
    public double valueAt(double x) {
        double value = functions[0].valueAt(x) - functions[1].valueAt(x);
        return value;
    }

    @Override
    public String toString() {
        String differenceString = "(" + functions[0].toString() + " - " + functions[1].toString() + ")";
        return differenceString;
    }

    @Override
    public Difference derivative() {
        return new Difference(functions[0].derivative(), functions[1].derivative());
    }
}
