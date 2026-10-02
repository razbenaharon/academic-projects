import java.util.HashMap;
import java.util.Map;
import java.lang.Thread;
import java.lang.IllegalMonitorStateException;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * The class represents a database which simulates the database. The class contains
 * An object of the HashMap type, where the database data is saved. The class constructor gets the maximum
 * number of threads that can read from the database at the same time. On top of that, the class implements an
 * operation called put that simulates writing to the database, as well as an operation called get that
 * simulates reading from it.
 */
public class Database {
    private Map<String, String> data;
    private final Lock lock;
    private final Condition readingCondition;
    private final Condition writingCondition;
    private boolean isSomeThreadWriting;
    private int numberOfReaders;
    private final int maxNumberOfReaders;

    public Database (int maxNumberOfReaders) {
        data = new HashMap<>();
        lock = new ReentrantLock();
        readingCondition = lock.newCondition();
        writingCondition = lock.newCondition();
        isSomeThreadWriting = false;
        numberOfReaders = 0;
        this.maxNumberOfReaders = maxNumberOfReaders;
    }

    /**
     * Operation that simulates writing to the database.
     * @param key - a key to write to.
     * @param value - a value to write into.
     */
    public void put (String key, String value) {
        data.put(key, value);
    }

    /**
     * Operation that simulates reading from the database.
     * @param key - a key to read from.
     */
    public String get (String key) {
        return data.get(key);
    }

    /**
     * An operation which is used before reading from the database. To an extent
     * And a thread will call this action when another thread writes to the database, or k other threads
     * Read from it, the thread will wait until it can read. The method catches the exception InterruptedException
     * in case it is thrown because of the 'await' method.
     */
    public void readAcquire () {
        lock.lock();
        try {
            while (isSomeThreadWriting == true || numberOfReaders >= maxNumberOfReaders) {
                readingCondition.await();
            }
            numberOfReaders++;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lock.unlock();
        }
    }

    /**
     * A Boolean operation which, like readAcquire, can also be used before
     * Reading from the database. This action is the same as the readAcquire action, but does not block the
     * thread until it can to read from the database, but returns true if the thread can start the reading and false
     * if it cannot.
     * @return result - A boolean value represents if the thread can start the reading or not.
     */
    public boolean readTryAcquire () {
        lock.lock();
        try {
            boolean result = ((!isSomeThreadWriting) && (numberOfReaders < maxNumberOfReaders));
            if (result == true) {
                numberOfReaders++;
                return result;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    /**
     * An operation which is used after reading from the database. The call to 'signal' represents
     * that the thread has finished reading from the database. If a thread uses this action but is not currently
     * reading an establishment the data, an exception of type IllegalMonitorStateException will be thrown with the
     * message "Illegal read release attempt". This exception is an unchecked exception already defined in Java.
     * @throws 'IllegalMonitorStateException' - If a thread uses this action but is not currently
     * reading an establishment the data, the exception will be thrown. This exception is an unchecked exception
     * already defined in Java.
     */
    public void readRelease () {
        lock.lock();
        try {
          if (numberOfReaders > 0) {
              numberOfReaders--;
                if (numberOfReaders < maxNumberOfReaders) {
                    readingCondition.signal();
                }
          }
          else {
              throw new IllegalMonitorStateException("Illegal read release attempt");
          }
        } finally {
            lock.unlock();
        }
    }

    /**
     * An operation which is used before writing to the database. To an extent
     * And a thread will call this method when another thread writes to the database, or there is another thread
     * reading From it, the thread will wait until it can write. The method catches the exception
     * 'InterruptedException' in case it is thrown because of the 'await' method.
     */
    public void writeAcquire () {
        lock.lock();
        try {
            while (isSomeThreadWriting == true || numberOfReaders > 0) {
                writingCondition.await();
            }
            isSomeThreadWriting = true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lock.unlock();
        }
    }

    /**
     * A boolean operation which, like writeAcquire, can also be used before writing to the database. This operation
     * is identical to the writeAcquire operation, but does not block the thread until it can write to the database,
     * but returns true if the thread can start writing and false if it cannot.
     * @return result - A boolean value represents if the thread can start the writing or not.
     */
    public boolean writeTryAcquire () {
        lock.lock();
        try {
            if (isSomeThreadWriting == true || numberOfReaders > 0) {
                return false;
            }
            isSomeThreadWriting = true;
            return true;
        } finally {
            lock.unlock();
        }
    }

    /**
     * An operation called writeRelease which is used after writing to the database. The call to method
     * Indicates that the thread has finished writing to the database. If a thread uses this method but it is not
     * the thread that writes currently to the database, an exception of type IllegalMonitorStateException will be
     * thrown with the message "Illegal write release attempt".
     * @throws 'IllegalMonitorStateException' - this exception will be thrown if a thread uses this method but it is
     * not the thread that writes currently to the database.
     */
    public void writeRelease () {
        lock.lock();
        try {
            if (isSomeThreadWriting == true) {
                isSomeThreadWriting = false;
                numberOfReaders = 0;
                writingCondition.signal();
                readingCondition.signalAll();
            }
            else {
                throw new IllegalMonitorStateException("Illegal write release attempt");
            }
        } finally {
            lock.unlock();
        }
    }
}