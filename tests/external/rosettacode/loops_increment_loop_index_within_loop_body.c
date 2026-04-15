// TEST: rosetta_loops_increment_loop_index_within_loop_body
// DESCRIPTION: Rosetta Code - Loops/Increment loop index within loop body (wrong_output)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Loops/Increment_loop_index_within_loop_body#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: n = 1                    43
// STDOUT: n = 2                    89
// STDOUT: n = 3                   179
// STDOUT: n = 4                   359
// STDOUT: n = 5                   719
// STDOUT: n = 6                  1439
// STDOUT: n = 7                  2879
// STDOUT: n = 8                  5779
// STDOUT: n = 9                 11579
// STDOUT: n = 10                23159
// STDOUT: n = 11                46327
// STDOUT: n = 12                92657
// STDOUT: n = 13               185323
// STDOUT: n = 14               370661
// STDOUT: n = 15               741337
// STDOUT: n = 16              1482707
// STDOUT: n = 17              2965421
// STDOUT: n = 18              5930887
// STDOUT: n = 19             11861791
// STDOUT: n = 20             23723597
// STDOUT: n = 21             47447201
// STDOUT: n = 22             94894427
// STDOUT: n = 23            189788857
// STDOUT: n = 24            379577741
// STDOUT: n = 25            759155483
// STDOUT: n = 26           1518310967
// STDOUT: n = 27           3036621941
// STDOUT: n = 28           6073243889
// STDOUT: n = 29          12146487779
// STDOUT: n = 30          24292975649
// STDOUT: n = 31          48585951311
// STDOUT: n = 32          97171902629
// STDOUT: n = 33         194343805267
// STDOUT: n = 34         388687610539
// STDOUT: n = 35         777375221081
// STDOUT: n = 36        1554750442183
// STDOUT: n = 37        3109500884389
// STDOUT: n = 38        6219001768781
// STDOUT: n = 39       12438003537571
// STDOUT: n = 40       24876007075181
// STDOUT: n = 41       49752014150467
// STDOUT: n = 42       99504028301131

#include <stdio.h>
#include <locale.h>

#define LIMIT 42

int is_prime(long long n) {
    if (n % 2 == 0) return n == 2;
    if (n % 3 == 0) return n == 3;
    long long d = 5;
    while (d * d <= n) {
        if (n % d == 0) return 0;
        d += 2;
        if (n % d == 0) return 0;
        d += 4;
    }
    return 1;
}

int main() {
    long long i;
    int n;
    setlocale(LC_NUMERIC, "");
    for (i = LIMIT, n = 0; n < LIMIT; i++)
        if (is_prime(i)) {
            n++;
            printf("n = %-2d  %'19lld\n", n, i);
            i += i - 1;
        }
    return 0;
}