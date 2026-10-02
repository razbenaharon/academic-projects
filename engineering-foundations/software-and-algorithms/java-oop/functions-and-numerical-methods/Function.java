public abstract class Function {
    public abstract String toString();
    public abstract double valueAt(double x);
    public abstract Function derivative();
    public Polynomial taylorPolynomial(int n) {
        TaylorPolynomial taylor = new TaylorPolynomial(this);
        return taylor.taylorPolynomial(n);
    }
    public double bisectionMethod(double a, double b, double epsilon) {
        bisectionMethod root = new bisectionMethod(this);
        return root.bisectionMethod(a, b, epsilon);
    }
    public double bisectionMethod(double a, double b) {
        bisectionMethod root = new bisectionMethod(this);
        return root.bisectionMethod(a,b,0.00001);
    }
    public double newtonRaphsonMethod(double a, double epsilon) {
        newtonRaphsonMethod root = new newtonRaphsonMethod(this);
        return root.newtonRaphsonMethod(a, epsilon);
    }
    public double newtonRaphsonMethod(double a) {
        newtonRaphsonMethod root = new newtonRaphsonMethod(this);
        return root.newtonRaphsonMethod(a,0.00001);
    }
}
