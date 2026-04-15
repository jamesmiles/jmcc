// TEST: rosetta_minimum_positive_multiple_in_base_10_using_only_0_and_1
// DESCRIPTION: Rosetta Code - Minimum positive multiple in base 10 using only 0 and 1 (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Minimum_positive_multiple_in_base_10_using_only_0_and_1#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 1 * 1 = 1
// STDOUT: 2 * 5 = 10
// STDOUT: 3 * 37 = 111
// STDOUT: 4 * 25 = 100
// STDOUT: 5 * 2 = 10
// STDOUT: 6 * 185 = 1110
// STDOUT: 7 * 143 = 1001
// STDOUT: 8 * 125 = 1000
// STDOUT: 9 * 12345679 = 111111111
// STDOUT: 10 * 1 = 10
// STDOUT: 95 * 1158 = 110010
// STDOUT: 96 * 115625 = 11100000
// STDOUT: 97 * 114433 = 11100001
// STDOUT: 98 * 112245 = 11000010
// STDOUT: 99 * 1122334455667789 = 111111111111111111
// STDOUT: 100 * 1 = 100
// STDOUT: 101 * 1 = 101
// STDOUT: 102 * 9805 = 1000110
// STDOUT: 103 * 107767 = 11100001
// STDOUT: 104 * 9625 = 1001000
// STDOUT: 105 * 962 = 101010
// STDOUT: 297 * 3740778151889263 = 1111011111111111111
// STDOUT: 576 * 192901234375 = 111111111000000
// STDOUT: 594 * 18703890759446315 = 11110111111111111110
// STDOUT: 891 * 1247038284075321 = 1111111111111111011
// STDOUT: 909 * 1112333455567779 = 1011111111111111111
// STDOUT: 999 * 111222333444555666777889 = 111111111111111111111111111
// STDOUT: 1998 * 556111667222778333889445 = 1111111111111111111111111110
// STDOUT: 2079 * 481530111164555609 = 1001101101111111111111
// STDOUT: 2251 * 44913861 = 101101101111
// STDOUT: 2277 * 4879275850290343 = 11110111111111111011
// STDOUT: 2439 * 4100082415379299344449 = 10000101011110111101111111
// STDOUT: 2997 * 370740777814851888925963 = 1111110111111111111111111111
// STDOUT: 4878 * 20500412076896496722245 = 100001010111101111011111110

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

__int128 imax(__int128 a, __int128 b) {
    if (a > b) {
        return a;
    }
    return b;
}

__int128 ipow(__int128 b, __int128 n) {
    __int128 res;
    if (n == 0) {
        return 1;
    }
    if (n == 1) {
        return b;
    }
    res = b;
    while (n > 1) {
        res *= b;
        n--;
    }
    return res;
}

__int128 imod(__int128 m, __int128 n) {
    __int128 result = m % n;
    if (result < 0) {
        result += n;
    }
    return result;
}

bool valid(__int128 n) {
    if (n < 0) {
        return false;
    }
    while (n > 0) {
        int r = n % 10;
        if (r > 1) {
            return false;
        }
        n /= 10;
    }
    return true;
}

__int128 mpm(const __int128 n) {
    __int128 *L;
    __int128 m, k, r, j;

    if (n == 1) {
        return 1;
    }

    L = calloc(n * n, sizeof(__int128));
    L[0] = 1;
    L[1] = 1;
    m = 0;
    while (true) {
        m++;
        if (L[(m - 1) * n + imod(-ipow(10, m), n)] == 1) {
            break;
        }
        L[m * n + 0] = 1;
        for (k = 1; k < n; k++) {
            L[m * n + k] = imax(L[(m - 1) * n + k], L[(m - 1) * n + imod(k - ipow(10, m), n)]);
        }
    }

    r = ipow(10, m);
    k = imod(-r, n);

    for (j = m - 1; j >= 1; j--) {
        if (L[(j - 1) * n + k] == 0) {
            r = r + ipow(10, j);
            k = imod(k - ipow(10, j), n);
        }
    }

    if (k == 1) {
        r++;
    }
    return r / n;
}

void print128(__int128 n) {
    char buffer[64]; // more then is needed, but is nice and round;
    int pos = (sizeof(buffer) / sizeof(char)) - 1;
    bool negative = false;

    if (n < 0) {
        negative = true;
        n = -n;
    }

    buffer[pos] = 0;
    while (n > 0) {
        int rem = n % 10;
        buffer[--pos] = rem + '0';
        n /= 10;
    }
    if (negative) {
        buffer[--pos] = '-';
    }
    printf(&buffer[pos]);
}

void test(__int128 n) {
    __int128 mult = mpm(n);
    if (mult > 0) {
        print128(n);
        printf(" * ");
        print128(mult);
        printf(" = ");
        print128(n * mult);
        printf("\n");
    } else {
        print128(n);
        printf("(no solution)\n");
    }
}

int main() {
    int i;

    // 1-10 (inclusive)
    for (i = 1; i <= 10; i++) {
        test(i);
    }
    // 95-105 (inclusive)
    for (i = 95; i <= 105; i++) {
        test(i);
    }
    test(297);
    test(576);
    test(594); // needs a larger number type (64 bits signed)
    test(891);
    test(909);
    test(999); // needs a larger number type (87 bits signed)

    // optional
    test(1998);
    test(2079);
    test(2251);
    test(2277);

    // stretch
    test(2439);
    test(2997);
    test(4878);

    return 0;
}