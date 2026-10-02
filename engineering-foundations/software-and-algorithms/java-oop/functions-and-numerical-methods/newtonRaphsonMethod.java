public class newtonRaphsonMethod extends Function{
    private Function function;

    public newtonRaphsonMethod(Function function) {
        this.function = function;
    }

    public double newtonRaphsonMethod(double a, double epsilon) {
        double x0 = a;
        double x1 = x0 - (this.function.valueAt(x0) / this.function.derivative().valueAt(x0));
        while ((Math.abs(this.function.valueAt(x1)) > epsilon) && ((x1-x0)!=0)) {
            x0 = x1;
            x1 = x0 - (this.function.valueAt(x0) / this.function.derivative().valueAt(x0));
        }
        return x1;
    }

    @Override
    public double newtonRaphsonMethod(double a) {
            double epsilon = 0.00001;
            double x0 = a;
            double x1 = x0 - (this.function.valueAt(x0) / this.function.derivative().valueAt(x0));
        while ((Math.abs(this.function.valueAt(x1)) > epsilon) && ((x1-x0)!=0)) {
                x0 = x1;
                x1 = x0 - (this.function.valueAt(x0) / this.function.derivative().valueAt(x0));
            }
            return x1;
        }


    @Override
    public String toString() {
        return "";
    }

    @Override
    public double valueAt(double x) {
        return 0.0;
    }

    @Override
    public Function derivative() {
        return null;
    }
    @Override
    public Polynomial taylorPolynomial(int n) {
        TaylorPolynomial taylor = new TaylorPolynomial(this);
        return taylor.taylorPolynomial(n);
    }
    @Override
    public double bisectionMethod(double a, double b, double epsilon) {
        bisectionMethod root = new bisectionMethod(this);
        return root.bisectionMethod(a, b, epsilon);
    }

    @Override
    public double bisectionMethod(double a, double b) {
        bisectionMethod root = new bisectionMethod(this);
        return root.bisectionMethod(a,b,0.00001);
    }

}