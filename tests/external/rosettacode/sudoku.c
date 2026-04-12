// TEST: rosetta_sudoku
// DESCRIPTION: Rosetta Code - Sudoku solver using backtracking
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Sudoku#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:
// STDOUT:   5 3 4  6 7 8  9 1 2
// STDOUT:   6 7 2  1 9 5  3 4 8
// STDOUT:   1 9 8  3 4 2  5 6 7
// STDOUT:
// STDOUT:   8 5 9  7 6 1  4 2 3
// STDOUT:   4 2 6  8 5 3  7 9 1
// STDOUT:   7 1 3  9 2 4  8 5 6
// STDOUT:
// STDOUT:   9 6 1  5 3 7  2 8 4
// STDOUT:   2 8 7  4 1 9  6 3 5
// STDOUT:   3 4 5  2 8 6  1 7 9

#include <stdio.h>

void show(int *x)
{
	int i, j;
	for (i = 0; i < 9; i++) {
		if (!(i % 3)) putchar('\n');
		for (j = 0; j < 9; j++)
			printf(j % 3 ? "%2d" : "%3d", *x++);
		putchar('\n');
	}
}

int trycell(int *x, int pos)
{
	int row = pos / 9;
	int col = pos % 9;
	int i, j, used = 0;

	if (pos == 81) return 1;
	if (x[pos]) return trycell(x, pos + 1);

	for (i = 0; i < 9; i++)
		used |= 1 << (x[i * 9 + col] - 1);

	for (j = 0; j < 9; j++)
		used |= 1 << (x[row * 9 + j] - 1);

	row = row / 3 * 3;
	col = col / 3 * 3;
	for (i = row; i < row + 3; i++)
		for (j = col; j < col + 3; j++)
			used |= 1 << (x[i * 9 + j] - 1);

	for (x[pos] = 1; x[pos] <= 9; x[pos]++, used >>= 1)
		if (!(used & 1) && trycell(x, pos + 1)) return 1;

	x[pos] = 0;
	return 0;
}

void solve(const char *s)
{
	int i, x[81];
	for (i = 0; i < 81; i++)
		x[i] = s[i] >= '1' && s[i] <= '9' ? s[i] - '0' : 0;

	if (trycell(x, 0))
		show(x);
	else
		puts("no solution");
}

int main(void)
{
	solve(	"5x..7...."
		"6..195..."
		".98....6."
		"8...6...3"
		"4..8.3..1"
		"7...2...6"
		".6....28."
		"...419..5"
		"....8..79"	);

	return 0;
}
