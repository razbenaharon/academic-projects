public class Polynomial extends Function {
    private double[] coefficients;

    public Polynomial(double... coefficients) {
        this.coefficients = coefficients;
    }

    @Override
    public String toString() {
        String polynomialString = "(";
        if (coefficients.length == 1 && coefficients[0] == 0) {
            polynomialString += "0)";
            return polynomialString;
        }
        int counter = 0;
        for (int i = 0; i < coefficients.length; i++) {
            if(coefficients[i] == 0) {
                counter++;
            }
        }
        if (counter == coefficients.length) {
            polynomialString += "0)";
            return polynomialString;
        }
        boolean flag = false;
        for (int i = 0; i < coefficients.length; i++) {
            double current = coefficients[i];
            if (current == 0.0) {
                continue;
            }
            else {
                if (current > 0.0) {
                    if (flag) {
                        polynomialString += " + ";
                    }
                }
                else {
                    if (flag) {
                        polynomialString += " - ";
                    }
                    else {
                        polynomialString += "-";
                    }
                    current = Math.abs(current);
                }
                flag = true;
                if (current == 1.0 && i > 0) {
                    if (i == 1) {
                        polynomialString += "x";
                    }
                    else {
                        polynomialString += "x^" + i;
                    }
                }
                else {
                    if (current % 1 == 0) {
                        polynomialString += String.format("%.0f", current);
                    }
                    else {
                        polynomialString += String.valueOf(current);
                    }
                    if (i > 0) {
                        polynomialString += "x";
                    }
                    if (i > 1) {
                        polynomialString += "^" + i;
                    }
                }
            }
        }
        polynomialString += ")";
        return polynomialString;
    }

    @Override
    public double valueAt(double x) {
        double value = 0;
        for (int i = 0; i < coefficients.length; i++) {
            value += coefficients[i] * Math.pow(x, i);
        }
        return value;
    }

    @Override
    public Polynomial derivative() {
        if (coefficients.length > 1) {
            double[] coefficientsOfDerivative = new double[coefficients.length - 1];
            for (int i = 1; i < coefficients.length; i++) {
                coefficientsOfDerivative[i - 1] = coefficients[i] * i;
            }
            return new Polynomial(coefficientsOfDerivative);
        }
        else{
            return new Constant(0);
        }
    }

}