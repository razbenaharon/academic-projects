public class Date {
    protected int day;
    protected int month;
    protected int year;

    public Date(int year, int month, int day){
        setYear(year);
        setMonth(month);
        setDay(day);
    }

    @Override
    public String toString(){
        String dateString = "";
        int digitsOfDay = numberOfDigits(day), digitsOfMonth = numberOfDigits(month),
                digitsOfYear = numberOfDigits(year);
        int numberofZerosInDay = 2 - digitsOfDay, numberOfZerosInMonth = 2 - digitsOfMonth,
                numberOfZerosInYear= 4 - digitsOfYear;
        for (int i = 0; i < numberofZerosInDay; i++) {
            dateString += "0";
        }
        dateString += this.day;
        dateString += "/";
        for (int i = 0; i < numberOfZerosInMonth; i++) {
            dateString += "0";
        }
        dateString += this.month;
        dateString += "/";
        for (int i = 0; i < numberOfZerosInYear; i++) {
            dateString += "0";
        }
        dateString += this.year;
        return dateString;
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (! (other instanceof Date) ) {
            return false;
        }
        if(this.hashCode()!=other.hashCode()) {
            return false;
        }
        Date otherDate = (Date) other;
        return this.day == otherDate.day && this.month == otherDate.month && this.year == otherDate.year;
    }

    @Override
    public int hashCode() {
        /**
         *preforms hash code to the functions. we multiply in 31(prime number) in order to avoid 2 different
         * dates with the same hash code.
         */
        int primeNumber = 17;
        primeNumber *= 31;
        primeNumber += day;
        primeNumber *= 31;
        primeNumber += month;
        primeNumber *= 31;
        primeNumber += year;
        return primeNumber;
    }

    public void setDay(int day) {
        if(day >= 1 && day <= 31) {
            this.day = day;
        }
        else {
            this.day = 1;
        }
    }

    public void setMonth(int month) {
        if(month >= 1 && month <= 12) {
            this.month = month;
        }
        else {
            this.month = 1;
        }
    }

    public void setYear(int year) {
        if(year >= -3999 && year <= 3999) {
            this.year = year;
        }
        else {
            this.year = 0;
        }
    }

    public int numberOfDigits(int number) {
        number = Math.abs(number);
        int counter=0;
        if(number==0) {
            return 1;
        }
        while(number > 0) {
            number /= 10;
            counter++;
        }
        return counter;
    }
}
