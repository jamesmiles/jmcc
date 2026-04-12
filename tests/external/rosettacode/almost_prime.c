// TEST: rosetta_almost_prime
// DESCRIPTION: Rosetta Code - Almost prime (k-almost primes)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Almost_prime#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: k = 1: 2 3 5 7 11 13 17 19 23 29
// STDOUT: k = 2: 4 6 9 10 14 15 21 22 25 26
// STDOUT: k = 3: 8 12 18 20 27 28 30 42 44 45
// STDOUT: k = 4: 16 24 36 40 54 56 60 81 84 88
// STDOUT: k = 5: 32 48 72 80 108 112 120 162 168 176

#include <stdio.h>

int kprime(int n, int k)
{
	int p, f = 0;
	for (p = 2; f < k && p*p <= n; p++)
		while (0 == n % p)
			n /= p, f++;

	return f + (n > 1) == k;
}

int main(void)
{
	int i, c, k;

	for (k = 1; k <= 5; k++) {
		printf("k = %d:", k);

		for (i = 2, c = 0; c < 10; i++)
			if (kprime(i, k)) {
				printf(" %d", i);
				c++;
			}

		putchar('\n');
	}

	return 0;
}
