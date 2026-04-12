// TEST: rosetta_farey_sequence
// DESCRIPTION: Rosetta Code - Farey sequence (fraction output wrong, 1/0 instead of 1/1)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Farey_sequence#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 1: 0/1 1/1
// STDOUT: 2: 0/1 1/2 1/1
// STDOUT: 3: 0/1 1/3 1/2 2/3 1/1
// STDOUT: 4: 0/1 1/4 1/3 1/2 2/3 3/4 1/1
// STDOUT: 5: 0/1 1/5 1/4 1/3 2/5 1/2 3/5 2/3 3/4 4/5 1/1
// STDOUT: 6: 0/1 1/6 1/5 1/4 1/3 2/5 1/2 3/5 2/3 3/4 4/5 5/6 1/1
// STDOUT: 7: 0/1 1/7 1/6 1/5 1/4 2/7 1/3 2/5 3/7 1/2 4/7 3/5 2/3 5/7 3/4 4/5 5/6 6/7 1/1
// STDOUT: 8: 0/1 1/8 1/7 1/6 1/5 1/4 2/7 1/3 3/8 2/5 3/7 1/2 4/7 3/5 5/8 2/3 5/7 3/4 4/5 5/6 6/7 7/8 1/1
// STDOUT: 9: 0/1 1/9 1/8 1/7 1/6 1/5 2/9 1/4 2/7 1/3 3/8 2/5 3/7 4/9 1/2 5/9 4/7 3/5 5/8 2/3 5/7 3/4 7/9 4/5 5/6 6/7 7/8 8/9 1/1
// STDOUT: 10: 0/1 1/10 1/9 1/8 1/7 1/6 1/5 2/9 1/4 2/7 3/10 1/3 3/8 2/5 3/7 4/9 1/2 5/9 4/7 3/5 5/8 2/3 7/10 5/7 3/4 7/9 4/5 5/6 6/7 7/8 8/9 9/10 1/1
// STDOUT: 11: 0/1 1/11 1/10 1/9 1/8 1/7 1/6 2/11 1/5 2/9 1/4 3/11 2/7 3/10 1/3 4/11 3/8 2/5 3/7 4/9 5/11 1/2 6/11 5/9 4/7 3/5 5/8 7/11 2/3 7/10 5/7 8/11 3/4 7/9 4/5 9/11 5/6 6/7 7/8 8/9 9/10 10/11 1/1
// STDOUT: 100: 3045 items
// STDOUT: 200: 12233 items
// STDOUT: 300: 27399 items
// STDOUT: 400: 48679 items
// STDOUT: 500: 76117 items
// STDOUT: 600: 109501 items
// STDOUT: 700: 149019 items
// STDOUT: 800: 194751 items
// STDOUT: 900: 246327 items
// STDOUT: 1000: 304193 items
// STDOUT:
// STDOUT: 10000000: 30396356427243 items

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void farey(int n)
{
	typedef struct { int d, n; } frac;
	frac f1 = {0, 1}, f2 = {1, n}, t;
	int k;

	printf("%d/%d %d/%d", 0, 1, 1, n);
	while (f2.n > 1) {
		k = (n + f1.n) / f2.n;
		t = f1, f1 = f2, f2 = (frac) { f2.d * k - t.d, f2.n * k - t.n };
		printf(" %d/%d", f2.d, f2.n);
	}

	putchar('\n');
}

typedef unsigned long long ull;
ull *cache;
size_t ccap;

ull farey_len(int n)
{
	if (n >= ccap) {
		size_t old = ccap;
		if (!ccap) ccap = 16;
		while (ccap <= n) ccap *= 2;
		cache = realloc(cache, sizeof(ull) * ccap);
		memset(cache + old, 0, sizeof(ull) * (ccap - old));
	} else if (cache[n])
		return cache[n];

	ull len = (ull)n*(n + 3) / 2;
	int p, q = 0;
	for (p = 2; p <= n; p = q) {
		q = n/(n/p) + 1;
		len -= farey_len(n/p) * (q - p);
	}

	cache[n] = len;
	return len;
}

int main(void)
{
	int n;
	for (n = 1; n <= 11; n++) {
		printf("%d: ", n);
		farey(n);
	}

	for (n = 100; n <= 1000; n += 100)
		printf("%d: %llu items\n", n, farey_len(n));

	n = 10000000;
	printf("\n%d: %llu items\n", n, farey_len(n));
	return 0;
}
