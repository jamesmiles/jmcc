// TEST: rosetta_determinant_and_permanent
// DESCRIPTION: Rosetta Code - Determinant and permanent (VLA, double**, recursion)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Determinant_and_permanent#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: det:               0
// STDOUT: perm:        6778800

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

double det_in(double **in, int n, int perm)
{
	if (n == 1) return in[0][0];

	double sum = 0, *m[--n];
	for (int i = 0; i < n; i++)
		m[i] = in[i + 1] + 1;

	for (int i = 0, sgn = 1; i <= n; i++) {
		sum += sgn * (in[i][0] * det_in(m, n, perm));
		if (i == n) break;

		m[i] = in[i] + 1;
		if (!perm) sgn = -sgn;
	}
	return sum;
}

/* wrapper function */
double det(double *in, int n, int perm)
{
	double *m[n];
	for (int i = 0; i < n; i++)
		m[i] = in + (n * i);

	return det_in(m, n, perm);
}

int main(void)
{
	double x[] = {	0, 1, 2, 3, 4,
			5, 6, 7, 8, 9,
			10, 11, 12, 13, 14,
			15, 16, 17, 18, 19,
			20, 21, 22, 23, 24 };

	printf("det:  %14.12g\n", det(x, 5, 0));
	printf("perm: %14.12g\n", det(x, 5, 1));

	return 0;
}
