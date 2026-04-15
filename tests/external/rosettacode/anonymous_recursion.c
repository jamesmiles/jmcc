// TEST: rosetta_anonymous_recursion
// DESCRIPTION: Rosetta Code - Anonymous recursion (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Anonymous_recursion#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Bad argument: fib(-1)
// STDOUT: fib -1 = -1
// STDOUT: fib 0 = 0
// STDOUT: fib 1 = 1
// STDOUT: fib 2 = 1
// STDOUT: fib 3 = 2
// STDOUT: calling fib_i from outside fib:
// STDOUT: This is not the fib you are looking for

#include <stdio.h>

long fib(long x)
{
        long fib_i(long n) { return n < 2 ? n : fib_i(n - 2) + fib_i(n - 1); };
        if (x < 0) {
                printf("Bad argument: fib(%ld)\n", x);
                return -1;
        }
        return fib_i(x);
}

long fib_i(long n) /* just to show the fib_i() inside fib() has no bearing outside it */
{
        printf("This is not the fib you are looking for\n");
        return -1;
}

int main()
{
        long x;
        for (x = -1; x < 4; x ++)
                printf("fib %ld = %ld\n", x, fib(x));

        printf("calling fib_i from outside fib:\n");
        fib_i(3);

        return 0;
}