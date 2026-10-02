public class MultiProduct extends Function {
    protected Function[] functions;
    protected Function function1;
    protected Function function2;
    public MultiProduct(Function function1, Function function2, Function... functions) {
        /**
         *by getting the functions like this, we can get 2 or more function in the input
         */
        this.function1 = function1;
        this.function2 = function2;
        this.functions = functions;
    }

    @Override
    public String toString() {
        String productString = "(";
        productString+=function1.toString()+ " * " + function2.toString();
        for (int i = 0; i < functions.length; i++) {
            productString += " * ";
            productString += functions[i].toString();
        }
        productString += ")";
        return productString;
    }

    @Override
    public double valueAt(double x) {
        double value = 1.0;
        value *= function1.valueAt(x);
        value *= function2.valueAt(x);
        for (Function function : functions) {
            value *= function.valueAt(x);
        }
        return value;
    }
    @Override
    public MultiSum derivative() {
        /**
         *preforms derivative of multi product functions-
         * first derivative of the first and the rest the same
         * then second func derivative and the rest the same
         * last we derivative the rest funcs that in the array (even if there is one)
         */
        Function function1_derivative = new MultiProduct(function1.derivative(), function2, functions);
        Function function2_derivative = new MultiProduct(function2.derivative(), function1, functions);
        Function function3_derivative;

        if (functions.length == 1) {
            function3_derivative = new MultiProduct(functions[0].derivative(), function1, function2);
            return new MultiSum(function1_derivative, function2_derivative, function3_derivative);
        }

            Function[] partsOfDerivative = new Function[functions.length];
            for (int i = 0; i < functions.length; i++) {
                Function[] currentProduct = new Function[functions.length];
                Function function_first_derivative = functions[i].derivative();
                int index = 1;
                for (int j = 0; j < functions.length; j++) {
                    if (i != j) {
                        currentProduct[0]=function2;
                        currentProduct[index] = functions[j];
                        index++;
                    }
                }
                partsOfDerivative[i] = new MultiProduct(function_first_derivative, function1, currentProduct);
            }

        return new MultiSum(function1_derivative, function2_derivative, partsOfDerivative);

    }

}

