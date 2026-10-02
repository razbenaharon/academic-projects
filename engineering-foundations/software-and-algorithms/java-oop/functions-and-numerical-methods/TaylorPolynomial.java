public class TaylorPolynomial extends Function {
    private Function function;

    public TaylorPolynomial(Function function) {
        this.function = function;
    }

    @Override
    public String toString() {
        return null;
    }

    @Override
    public double valueAt(double x) {
        return 0;
    }

    @Override
    public Function derivative() {
        return null;
    }
    public Polynomial taylorPolynomial ( int n) {
        Polynomial res;
        if (n == 0) {
            res = new Polynomial(function.valueAt(0));
        } else {
            double cur_factorial = 1;
            double[] functions = new double[n + 1];
            functions[0] = function.valueAt(0);
            Function deriviate = function.derivative();
            for (int i = 1; i <= n; i++) {
                cur_factorial *= i;
                functions[i] = deriviate.valueAt(0) / cur_factorial;
                deriviate = deriviate.derivative();
            }
            res = new Polynomial(functions);
        }
        return res;
    }
}
