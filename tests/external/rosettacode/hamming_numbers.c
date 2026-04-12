// TEST: rosetta_hamming_numbers
// DESCRIPTION: Rosetta Code - Hamming numbers (undeclared variable in nested scope)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Hamming_numbers#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:      1: 1
// STDOUT:      2: 2
// STDOUT:      3: 3
// STDOUT:      4: 4
// STDOUT:      5: 5
// STDOUT:      6: 6
// STDOUT:      7: 8
// STDOUT:      8: 9
// STDOUT:      9: 10
// STDOUT:     10: 12
// STDOUT:     11: 15
// STDOUT:     12: 16
// STDOUT:     13: 18
// STDOUT:     14: 20
// STDOUT:     15: 24
// STDOUT:     16: 25
// STDOUT:     17: 27
// STDOUT:     18: 30
// STDOUT:     19: 32
// STDOUT:     20: 36
// STDOUT:   1691: 2125764000

#include <stdio.h>
#include <stdlib.h>

typedef unsigned long long ham;

size_t alloc = 0, n = 1;
ham *q = 0;

void qpush(ham h)
{
	int i, j;
	if (alloc <= n) {
		alloc = alloc ? alloc * 2 : 16;
		q = realloc(q, sizeof(ham) * alloc);
	}

	for (i = n++; (j = i/2) && q[j] > h; q[i] = q[j], i = j);
	q[i] = h;
}

ham qpop()
{
	int i, j;
	ham r, t;
	/* outer loop for skipping duplicates */
	for (r = q[1]; n > 1 && r == q[1]; q[i] = t) {
		/* inner loop is the normal down heap routine */
		for (i = 1, t = q[--n]; (j = i * 2) < n;) {
			if (j + 1 < n && q[j] > q[j+1]) j++;
			if (t <= q[j]) break;
			q[i] = q[j], i = j;
		}
	}

	return r;
}

int main()
{
	int i;
	ham h;

	for (qpush(i = 1); i <= 1691; i++) {
		/* takes smallest value, and queue its multiples */
		h = qpop();
		qpush(h * 2);
		qpush(h * 3);
		qpush(h * 5);

		if (i <= 20 || i == 1691)
			printf("%6d: %llu\n", i, h);
	}

	/* free(q); */
	return 0;
}
