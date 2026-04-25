// On macOS ARM64, setlocale(LC_NUMERIC, "") activates the system locale which
// uses comma thousands-separators for %'d formatting, whereas on Linux x86-64
// the default "C" locale produces plain digits without separators.
// TEST: rosetta_loops_with_multiple_ranges
// DESCRIPTION: Rosetta Code - Loops/With multiple ranges (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Loops/With_multiple_ranges#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: sum  =  348173
// STDOUT: prod = -793618560
// EXPECTED_STDOUT_ARM64:
// STDOUT_ARM64: sum  =  348,173
// STDOUT_ARM64: prod = -793,618,560

#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

long prod = 1L, sum = 0L;

void process(int j) {
    sum += abs(j);
    if (labs(prod) < (1 << 27) && j) prod *= j;
}

long ipow(int n, uint e) {
    long pr = n;
    int i;
    if (e == 0) return 1L;
    for (i = 2; i <= e; ++i) pr *= n;
    return pr;
}

int main() {
    int j;
    const int x = 5, y = -5, z = -2;
    const int one = 1, three = 3, seven = 7;
    long p = ipow(11, x);
    for (j = -three; j <= ipow(3, 3); j += three) process(j);
    for (j = -seven; j <= seven; j += x) process(j);
    for (j = 555; j <= 550 - y; ++j) process(j);
    for (j = 22; j >= -28; j -= three) process(j);
    for (j = 1927; j <= 1939; ++j) process(j);
    for (j = x; j >= y; j -= -z) process(j);
    for (j = p; j <= p + one; ++j) process(j);
    setlocale(LC_NUMERIC, "");
    printf("sum  = % 'ld\n", sum);
    printf("prod = % 'ld\n", prod);
    return 0;
}