public class Quotient extends Function {
    private Function[] functions;

    public Quotient(Function... functions) {
        this.functions = functions;
    }

    @Override
    public double valueAt(double x) {
        return (functions[0].valueAt(x)/functions[1].valueAt(x));
    }

    @Override
    public String toString() {
        String quotientString = "(" + functions[0].toString() + " / " + functions[1].toString() + ")";
        return quotientString;
    }

    @Override
    public Quotient derivative() {
        Function numeratorDerivative = functions[0].derivative();
        Function denominatorDerivative = functions[1].derivative();
        Function product1 = new Product(numeratorDerivative, functions[1]);
        Function product2 = new Product(denominatorDerivative, functions[0]);
        Function totalNumerator = new Difference(product1, product2);
        double constantTwo = 2;
        Function totalDenominator = new Power(functions[1], constantTwo);
        return new Quotient(totalNumerator, totalDenominator);
    }
}
