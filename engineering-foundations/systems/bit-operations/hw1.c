#include <stdio.h>

int main() {

    return 0;
}


int bitAnd(int x, int y) {

    //using de-morgan when open ()

    return ~(~x | ~y);
}


int getByte(int x, int n) {

    // multiply n by 2^3 (moving 3).
    // creating int mask of 24 0's and 8 1's after (1 byte)
    // move the n byte of x to the LSB
    // do bitwise and with mask in order to rescue this byte and the rest bytes are zero

    int num_of_moves = n << 3;
    int mask = 0xFF;
    int byte = (x >> num_of_moves) & mask;

    return byte;
}

int logicalShift(int x, int n) {

    // first we move 1 to the most left bit and the rest are 0
    // than by moving n to the right and 1 to the left we make n time 1 on the ledt and 32-n 0 after
    // that by bitwise not we make n 0's on left and 32-n 1's on the right
    // than we make bitwise and with x shifted n time and the mask in order to make
    // sure that the 32-n bits in the left to be zero

    int mask = (1 << 31);
    mask = (mask >> n) << 1;
    mask = ~mask;


    return ((x >> n) & mask);
}
