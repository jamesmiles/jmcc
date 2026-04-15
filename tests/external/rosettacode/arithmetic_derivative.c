// TEST: rosetta_arithmetic_derivative
// DESCRIPTION: Rosetta Code - Arithmetic derivative (wrong_output)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Arithmetic_derivative#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:  -75  -77   -1 -272  -24  -49  -34  -96  -20 -123 
// STDOUT:   -1 -140  -32  -45  -22 -124   -1  -43 -108 -176 
// STDOUT:   -1  -71  -18  -80  -55  -39   -1 -156   -1  -59 
// STDOUT:  -26  -72   -1  -61  -18 -192  -51  -33   -1  -92 
// STDOUT:   -1  -31  -22  -92  -16  -81   -1  -56  -20  -45 
// STDOUT:  -14 -112   -1  -25  -39  -48   -1  -41   -1  -68 
// STDOUT:  -16  -21   -1  -60  -12  -19  -14  -80   -1  -31 
// STDOUT:   -1  -32  -27  -15  -10  -44   -1  -13  -10  -24 
// STDOUT:   -1  -21   -1  -32   -8   -9   -1  -16   -1   -7 
// STDOUT:   -6  -12   -1   -5   -1   -4   -1   -1    0    0 
// STDOUT:    0    1    1    4    1    5    1   12    6    7 
// STDOUT:    1   16    1    9    8   32    1   21    1   24 
// STDOUT:   10   13    1   44   10   15   27   32    1   31 
// STDOUT:    1   80   14   19   12   60    1   21   16   68 
// STDOUT:    1   41    1   48   39   25    1  112   14   45 
// STDOUT:   20   56    1   81   16   92   22   31    1   92 
// STDOUT:    1   33   51  192   18   61    1   72   26   59 
// STDOUT:    1  156    1   39   55   80   18   71    1  176 
// STDOUT:  108   43    1  124   22   45   32  140    1  123 
// STDOUT:   20   96   34   49   24  272    1   77   75  140 
// STDOUT:
// STDOUT: D(10^1 ) / 7 = 1
// STDOUT: D(10^2 ) / 7 = 20
// STDOUT: D(10^3 ) / 7 = 300
// STDOUT: D(10^4 ) / 7 = 4000
// STDOUT: D(10^5 ) / 7 = 50000
// STDOUT: D(10^6 ) / 7 = 600000
// STDOUT: D(10^7 ) / 7 = 7000000
// STDOUT: D(10^8 ) / 7 = 80000000
// STDOUT: D(10^9 ) / 7 = 900000000
// STDOUT: D(10^10) / 7 = 10000000000
// STDOUT: D(10^11) / 7 = 110000000000
// STDOUT: D(10^12) / 7 = 1200000000000
// STDOUT: D(10^13) / 7 = 13000000000000
// STDOUT: D(10^14) / 7 = 140000000000000
// STDOUT: D(10^15) / 7 = 1500000000000000
// STDOUT: D(10^16) / 7 = 16000000000000000
// STDOUT: D(10^17) / 7 = 170000000000000000
// STDOUT: D(10^18) / 7 = 1800000000000000000
// STDOUT: D(10^19) / 7 = 19000000000000000000
// STDOUT: D(10^20) / 7 = 200000000000000000000

#include <stdio.h>
#include <stdint.h>

typedef uint64_t u64;

void primeFactors(u64 n, u64 *factors, int *length) {
    if (n < 2) return;
    int count = 0;
    int inc[8] = {4, 2, 4, 2, 4, 6, 2, 6};
    while (!(n%2)) {
        factors[count++] = 2;
        n /= 2;
    }
    while (!(n%3)) {
        factors[count++] = 3;
        n /= 3;
    }
    while (!(n%5)) {
        factors[count++] = 5;
        n /= 5;
    }
    for (u64 k = 7, i = 0; k*k <= n; ) {
        if (!(n%k)) {
            factors[count++] = k;
            n /= k;
        } else {
            k += inc[i];
            i = (i + 1) % 8;
        }
    }
    if (n > 1) {
        factors[count++] = n;
    }
    *length = count;
}

double D(double n) {
    if (n < 0) return -D(-n);
    if (n < 2) return 0;
    int i, length;
    double d;
    u64 f[80], g;
    if (n < 1e19) {
        primeFactors((u64)n, f, &length);
    } else {
        g = (u64)(n / 100);
        primeFactors(g, f, &length);
        f[length+1] = f[length] = 2;
        f[length+3] = f[length+2] = 5;
        length += 4;
    }
    if (length == 1) return 1;
    if (length == 2) return (double)(f[0] + f[1]);
    d = n / (double)f[0];
    return D(d) * (double)f[0] + d;
}

int main() {
    u64 ad[200];
    int n, m;
    double pow;
    for (n = -99; n < 101; ++n) {
        ad[n+99] = (int)D((double)n);
    }
    for (n = 0; n < 200; ++n) {
        printf("%4ld ", ad[n]);
        if (!((n+1)%10)) printf("\n");
    }
    printf("\n");
    pow = 1;
    for (m = 1; m < 21; ++m) {
        pow *= 10;
        printf("D(10^%-2d) / 7 = %.0f\n", m, D(pow)/7);
    }
    return 0;
}