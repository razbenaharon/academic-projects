public class Power extends Function {
    private Function function;
    private double power;
    public Power(Function function, double power) {
        this.function = function;
        this.power = power;
    }

    @Override
    public double valueAt(double x) {
        return Math.pow(function.valueAt(x), power);
    }

    @Override
    public String toString() {
        String powerString = "(" + function.toString() + "^" + String.format("%.0f", power) + ")";
        return powerString;
    }

    @Override
    public MultiProduct derivative() {
        if (power == 1) {
            double one = 1;
            Function constOfOne = new Constant(one);
            return new MultiProduct(function.derivative(), constOfOne);
        }
        else {
            Function powerFunction = new Constant(power);
            double powerMinusOne = power - 1;
            Function derivativeOfFunction = function.derivative();
            Function functionPowerMinusOne = new Power(function, powerMinusOne);
            return new MultiProduct(powerFunction, functionPowerMinusOne, derivativeOfFunction);
        }
    }

}
