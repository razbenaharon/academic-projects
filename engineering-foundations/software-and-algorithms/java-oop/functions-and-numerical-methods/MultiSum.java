public class MultiSum extends Function {
    protected Function[] functions;
    protected Function function1;
    protected Function function2;

    public MultiSum(Function function1, Function function2, Function... functions) {
        this.function1 = function1;
        this.function2 = function2;
        this.functions = functions;
    }

    @Override
    public MultiSum derivative() {
        Function[] multiSumOfDerivation = new Function[functions.length];

        for (int i = 0; i < functions.length; i++) {
            multiSumOfDerivation[i] = functions[i].derivative();
        }

        return new MultiSum(this.function1.derivative(), this.function2.derivative(), multiSumOfDerivation);
    }

    @Override
    public double valueAt(double x) {
        double value = 0.0;
        value += function1.valueAt(x);
        value += function2.valueAt(x);
        for (Function function : functions) {
            value += function.valueAt(x);
        }

        return value;
    }

    @Override
    public String toString() {
        String sumString = "(";
        sumString+=function1.toString()+ " + " + function2.toString();
        for(int i = 0; i < functions.length; i++) {
            sumString += " + ";
            sumString += functions[i].toString();
        }
        sumString += ")";
        return sumString;
    }

}