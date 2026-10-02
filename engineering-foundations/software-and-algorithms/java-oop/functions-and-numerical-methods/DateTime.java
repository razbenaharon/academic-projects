public class DateTime extends Date {
    private int hour;
    private int minute;
    public DateTime(int day, int month, int year, int hour, int minute) {
        super(day, month, year);
        setHour(hour);
        setMinute(minute);
    }
    @Override
    public String toString() {
        String dateTimeString = "";
        int digitsOfDay = numberOfDigits(day), digitsOfMonth = numberOfDigits(month),
                digitsOfYear = numberOfDigits(year), digitsOfHour = numberOfDigits(hour),
                digitsOfMinute = numberOfDigits(minute);
        int numberZerosInDay=2-digitsOfDay, numberZerosInMonth=2-digitsOfMonth,
                numberZerosInYear=4-digitsOfYear,
                numberZerosInHour=2-digitsOfHour, numberZerosInMinute=2-digitsOfMinute;
        for (int i = 0; i < numberZerosInDay; i++) {
            dateTimeString += "0";
        }
        dateTimeString += this.day;
        dateTimeString += "/";
        for (int i = 0; i < numberZerosInMonth; i++) {
            dateTimeString += "0";
        }
        dateTimeString += this.month;
        dateTimeString += "/";
        for (int i = 0; i < numberZerosInYear; i++) {
            dateTimeString += "0";
        }
        dateTimeString += this.year;
        dateTimeString += " ";
        for (int i = 0; i < numberZerosInHour; i++) {
            dateTimeString += "0";
        }
        dateTimeString += this.hour;
        dateTimeString += ":";
        for (int i = 0; i < numberZerosInMinute; i++) {
            dateTimeString += "0";
        }
        dateTimeString += this.minute;
        return dateTimeString;
    }

    @Override
    public boolean equals(Object other) {
        if(this == other) {
            return true;
        }
        if(! (other instanceof DateTime) ) {
            return false;
        }
        DateTime otherDate = (DateTime) other;
        return (this.day == otherDate.day && this.month == otherDate.month && this.year == otherDate.year && this.hour == otherDate.hour && this.minute == otherDate.minute);
    }

    @Override
    public int hashCode() {
        int primeNumber = super.hashCode();
        primeNumber *= 31;
        primeNumber += hour;
        primeNumber *= 31;
        primeNumber += minute;
        return primeNumber;
    }

    public void setHour(int hour) {
        if(hour >= 0 && hour <= 23) {
            this.hour = hour;
        }
        else {
            this.hour = 0;
        }
    }

    public void setMinute(int minute) {
        if(minute >= 0 && minute <= 59) {
            this.minute = minute;
        }
        else {
            this.minute = 0;
        }
    }
}
