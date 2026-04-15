// TEST: rosetta_price_fraction
// DESCRIPTION: Rosetta Code - Price fraction (exit_-6)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Price_fraction#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 0.00 0.10
// STDOUT: 0.01 0.10
// STDOUT: 0.02 0.10
// STDOUT: 0.03 0.10
// STDOUT: 0.04 0.10
// STDOUT: 0.05 0.10
// STDOUT: 0.06 0.18
// STDOUT: 0.07 0.18
// STDOUT: 0.08 0.18
// STDOUT: 0.09 0.18
// STDOUT: 0.10 0.18
// STDOUT: 0.11 0.26
// STDOUT: 0.12 0.26
// STDOUT: 0.13 0.26
// STDOUT: 0.14 0.26
// STDOUT: 0.15 0.26
// STDOUT: 0.16 0.32
// STDOUT: 0.17 0.32
// STDOUT: 0.18 0.32
// STDOUT: 0.19 0.32
// STDOUT: 0.20 0.32
// STDOUT: 0.21 0.38
// STDOUT: 0.22 0.38
// STDOUT: 0.23 0.38
// STDOUT: 0.24 0.38
// STDOUT: 0.25 0.38
// STDOUT: 0.26 0.44
// STDOUT: 0.27 0.44
// STDOUT: 0.28 0.44
// STDOUT: 0.29 0.44
// STDOUT: 0.30 0.44
// STDOUT: 0.31 0.50
// STDOUT: 0.32 0.50
// STDOUT: 0.33 0.50
// STDOUT: 0.34 0.50
// STDOUT: 0.35 0.50
// STDOUT: 0.36 0.54
// STDOUT: 0.37 0.54
// STDOUT: 0.38 0.54
// STDOUT: 0.39 0.54
// STDOUT: 0.40 0.54
// STDOUT: 0.41 0.58
// STDOUT: 0.42 0.58
// STDOUT: 0.43 0.58
// STDOUT: 0.44 0.58
// STDOUT: 0.45 0.58
// STDOUT: 0.46 0.62
// STDOUT: 0.47 0.62
// STDOUT: 0.48 0.62
// STDOUT: 0.49 0.62
// STDOUT: 0.50 0.62
// STDOUT: 0.51 0.66
// STDOUT: 0.52 0.66
// STDOUT: 0.53 0.66
// STDOUT: 0.54 0.66
// STDOUT: 0.55 0.66
// STDOUT: 0.56 0.70
// STDOUT: 0.57 0.70
// STDOUT: 0.58 0.70
// STDOUT: 0.59 0.70
// STDOUT: 0.60 0.70
// STDOUT: 0.61 0.74
// STDOUT: 0.62 0.74
// STDOUT: 0.63 0.74
// STDOUT: 0.64 0.74
// STDOUT: 0.65 0.74
// STDOUT: 0.66 0.78
// STDOUT: 0.67 0.78
// STDOUT: 0.68 0.78
// STDOUT: 0.69 0.78
// STDOUT: 0.70 0.78
// STDOUT: 0.71 0.82
// STDOUT: 0.72 0.82
// STDOUT: 0.73 0.82
// STDOUT: 0.74 0.82
// STDOUT: 0.75 0.82
// STDOUT: 0.76 0.86
// STDOUT: 0.77 0.86
// STDOUT: 0.78 0.86
// STDOUT: 0.79 0.86
// STDOUT: 0.80 0.86
// STDOUT: 0.81 0.90
// STDOUT: 0.82 0.90
// STDOUT: 0.83 0.90
// STDOUT: 0.84 0.90
// STDOUT: 0.85 0.90
// STDOUT: 0.86 0.94
// STDOUT: 0.87 0.94
// STDOUT: 0.88 0.94
// STDOUT: 0.89 0.94
// STDOUT: 0.90 0.94
// STDOUT: 0.91 0.98
// STDOUT: 0.92 0.98
// STDOUT: 0.93 0.98
// STDOUT: 0.94 0.98
// STDOUT: 0.95 0.98
// STDOUT: 0.96 1.00
// STDOUT: 0.97 1.00
// STDOUT: 0.98 1.00
// STDOUT: 0.99 1.00
// STDOUT: 1.00 1.00

#include<stdio.h>

double table[][2] = {
	{0.06, 0.10}, {0.11, 0.18}, {0.16, 0.26}, {0.21, 0.32},
	{0.26, 0.38}, {0.31, 0.44}, {0.36, 0.50}, {0.41, 0.54},
	{0.46, 0.58}, {0.51, 0.62}, {0.56, 0.66}, {0.61, 0.70},
	{0.66, 0.74}, {0.71, 0.78}, {0.76, 0.82}, {0.81, 0.86},
	{0.86, 0.90}, {0.91, 0.94}, {0.96, 0.98}, {1.01, 1.00},
	{-1, 0}, /* guarding element */
};

double price_fix(double x)
{
	int i;
	for (i = 0; table[i][0] > 0; i++)
		if (x < table[i][0]) return table[i][1];

	abort(); /* what else to do? */
}

int main()
{
	int i;
	for (i = 0; i <= 100; i++)
		printf("%.2f %.2f\n", i / 100., price_fix(i / 100.));

	return 0;
}