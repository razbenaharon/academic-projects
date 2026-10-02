import java.util.Iterator;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

/**
 * The class represents Stack which is represented as an array of the Cloneable type, converted to the
 * generic type E when needed.
 * @param <E> - The generic type E.
 */
public class ArrayStack<E extends Cloneable> implements Stack<E>, Cloneable, Iterable<E> {
    private final int capacity;
    private Cloneable[] elements;
    private int currentSize;

    /**
     * A constructor for the ArrayStack class.
     * @param capacity - the capacity of the stack.
     */
    public ArrayStack (int capacity) {
        if(capacity < 0) {
            throw new NegativeCapacityException("Negative value inserted");
        }
        this.capacity = capacity;
        this.currentSize = 0;
        this.elements = new Cloneable[capacity];
    }

    /**
     * A method that receives an element and adds it to head of the stack.
     * @param element - An element of the stack.
     */
    @Override
    public void push (E element) {
        if (isStackFull() == true) {
            throw new StackOverflowException("The stack is in it's full capacity");
        }
        elements[currentSize] = element;
        currentSize++;
    }

    /**
     * A method that returns true if the stack is completely full, that is, the current size of the stack
     * (the number of elements in it) is equal to its capacity.
     * @return a boolean variable for whether the stack is full (will be true) or not (will be false).
     */
    public boolean isStackFull () {
        if (currentSize == capacity) {
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * A method that removes an element from the head of the stack and returns it.
     * @return The current element in the head of the stack.
     */
    @Override
    public E pop () {
        if (isEmpty() == true) {
            throw new EmptyStackException("The stack is empty");
        }
        E headElement = (E) elements[currentSize - 1];
        elements[currentSize-1] = null;
        currentSize--;
        return headElement;
    }

    /**
     * A method that returns the element that is at the head of the stack, without removing it.
     * @return The current element in the head of the stack.
     */
    @Override
    public E peek () {
        if (isEmpty() == true) {
            throw new EmptyStackException("The stack is empty");
        }
        return (E) elements[currentSize - 1];
    }

    /**
     * A method that returns the number of elements in the stack.
     * @return The number of elements in the stack.
     */
    @Override
    public int size () {
        return currentSize;
    }

    /**
     * A method that checks whether there are elements in the stack and returns the result.
     * @return a boolean variable for whether there are elements in the stack or not.
     */
    @Override
    public boolean isEmpty () {
        if (currentSize == 0) {
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * A method that performs a deep copy of the stack. The method performs a loop in which in
     * each iteration a single element is sent to another method, when the method performs a deep copy
     * on that single element.
     * @return A stack as an array of the generic type E. This is the replicated array to which
     * a deep copy was performed.
     */
    @Override
    public ArrayStack<E> clone () {
        try {
            ArrayStack<E> cloneStack = (ArrayStack<E>) super.clone();
            cloneStack.elements = elements.clone();
            for (int i = 0; i < currentSize; i++) {
                cloneStack.elements[i] = cloneSingleElement(elements[i]);
            }
            return cloneStack;
        } catch (CloneNotSupportedException e) {
            return null;
        }
    }

    /**
     * A method that performs a deep copy on a single member with the help of the getMethod
     * and invoke methods while understanding the exceptions that may arise from the use of
     * these methods.
     * @param element - A single element of the stack to which a deep copy is performed.
     * @return The element created from the deep copy of the single element.
     */
    public E cloneSingleElement (Cloneable element) {
        try {
            Method cloneMethod = element.getClass().getMethod("clone");
            return (E) cloneMethod.invoke(element);
        } catch (InvocationTargetException | NoSuchMethodException | IllegalAccessException e) {
            return null;
        }
    }

    /**
     * Iterator which will be used to move over the elements of the stack. The elements will be
     * moved in the order they appear in the stack, starting with the element
     * which is at the top of the stack and up to the element at the tail.
     * @return The iterator.
     */
    public Iterator<E> iterator () {
        return new StackIterator();
    }

    /**
     * The implementation of the iterator itself and the implementation of the interface Iterator.
     */
    private class StackIterator implements Iterator<E> {
        private int currentIndex;
        public StackIterator () {
            this.currentIndex = currentSize - 1;
        }

        /**
         * A method that returns true if there are other elements that are before the element
         * to which the currentIndex refers (that is, closer to the tail of the stack).
         */
        @Override
        public boolean hasNext () {
            if (currentIndex < 0) {
                return false;
            }
            else {
                return true;
            }
        }

        /**
         * A method that returns the next element in the stack (that is, closest to the tail of the stack).
         * When returning, the element is converted to the generic type E, and if the method hasNext returns
         * false, we will return a null value since the next element in the stack does not exist.
         */
        @Override
        public E next () {
            if (hasNext() == false) {
                return null;
            }
            Cloneable currentElement = elements[currentIndex];
            currentIndex--;
            return (E) currentElement;
        }
    }
}