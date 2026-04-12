// TEST: rosetta_matrix_transposition
// DESCRIPTION: Rosetta Code - Matrix transposition (VLA pointers to double arrays)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Matrix_transposition#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 0 5 1
// STDOUT: 1 6 0
// STDOUT: 2 7 0
// STDOUT: 3 8 0
// STDOUT: 4 9 42

#include <stdio.h>

void transpose(void *dest, void *src, int src_h, int src_w)
{
	int i, j;
	double (*d)[src_h] = dest, (*s)[src_w] = src;
	for (i = 0; i < src_h; i++)
		for (j = 0; j < src_w; j++)
			d[j][i] = s[i][j];
}

int main()
{
	int i, j;
	double a[3][5] = {{ 0, 1, 2, 3, 4 },
			  { 5, 6, 7, 8, 9 },
			  { 1, 0, 0, 0, 42}};
	double b[5][3];
	transpose(b, a, 3, 5);

	for (i = 0; i < 5; i++)
		for (j = 0; j < 3; j++)
			printf("%g%c", b[i][j], j == 2 ? '\n' : ' ');
	return 0;
}
