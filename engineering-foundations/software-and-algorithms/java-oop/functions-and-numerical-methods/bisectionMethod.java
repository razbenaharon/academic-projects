public class bisectionMethod extends Function{
    private Function function;

    public bisectionMethod(Function function) {
        this.function = function;
    }

    public double bisectionMethod(double a, double b, double epsilon) {
        double left = a;
        double right = b;

        while ((right - left) > epsilon) {
            double mid = (left + right) / 2;
            double fLeft = this.function.valueAt(left);
            double fMid = this.function.valueAt(mid);
            if (fLeft * fMid > 0) {
                left = mid;
            } else {
                right = mid;
            }
        }
        return (left + right) / 2;
    }


    public double bisectionMethod(double a, double b) {
        double left = a;
        double right = b;
        double epsilon = 0.00001;

        while ((right - left) > epsilon) {
            double mid = (left + right) / 2;
            double fLeft = this.function.valueAt(left);
            double fMid = this.function.valueAt(mid);
            if (fLeft * fMid > 0) {
                left = mid;
            } else {
                right = mid;
            }
        }

        return (left + right) / 2;
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
    public double newtonRaphsonMethod(double a, double epsilon) {
        newtonRaphsonMethod root = new newtonRaphsonMethod(this);
        return root.newtonRaphsonMethod(a, epsilon);
    }

    @Override
    public double newtonRaphsonMethod(double a) {
        newtonRaphsonMethod root = new newtonRaphsonMethod(this);
        return root.newtonRaphsonMethod(a,0.00001);
    }

}

