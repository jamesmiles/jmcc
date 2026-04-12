// TEST: rosetta_cut_a_rectangle
// DESCRIPTION: Rosetta Code - Cut a rectangle (VLA with brackets in param)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Cut_a_rectangle#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 2 x 1: 1
// STDOUT: 2 x 2: 2
// STDOUT: 3 x 2: 3
// STDOUT: 4 x 1: 1
// STDOUT: 4 x 2: 4
// STDOUT: 4 x 3: 9
// STDOUT: 4 x 4: 22
// STDOUT: 5 x 2: 5
// STDOUT: 5 x 4: 39
// STDOUT: 6 x 1: 1
// STDOUT: 6 x 2: 6
// STDOUT: 6 x 3: 23
// STDOUT: 6 x 4: 90
// STDOUT: 6 x 5: 263
// STDOUT: 6 x 6: 1018
// STDOUT: 7 x 2: 7
// STDOUT: 7 x 4: 151
// STDOUT: 7 x 6: 2947
// STDOUT: 8 x 1: 1
// STDOUT: 8 x 2: 8
// STDOUT: 8 x 3: 53
// STDOUT: 8 x 4: 340
// STDOUT: 8 x 5: 1675
// STDOUT: 8 x 6: 11174
// STDOUT: 8 x 7: 55939
// STDOUT: 8 x 8: 369050
// STDOUT: 9 x 2: 9
// STDOUT: 9 x 4: 553
// STDOUT: 9 x 6: 31721
// STDOUT: 9 x 8: 1812667
// STDOUT: 10 x 1: 1
// STDOUT: 10 x 2: 10
// STDOUT: 10 x 3: 115
// STDOUT: 10 x 4: 1228
// STDOUT: 10 x 5: 10295
// STDOUT: 10 x 6: 118276
// STDOUT: 10 x 7: 1026005
// STDOUT: 10 x 8: 11736888
// STDOUT: 10 x 9: 99953769
// STDOUT: 10 x 10: 1124140214

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char byte;
byte *grid = 0;

int w, h, len;
unsigned long long cnt;

static int next[4], dir[4][2] = {{0, -1}, {-1, 0}, {0, 1}, {1, 0}};
void walk(int y, int x)
{
	int i, t;

	if (!y || y == h || !x || x == w) {
		cnt += 2;
		return;
	}

	t = y * (w + 1) + x;
	grid[t]++, grid[len - t]++;

	for (i = 0; i < 4; i++)
		if (!grid[t + next[i]])
			walk(y + dir[i][0], x + dir[i][1]);

	grid[t]--, grid[len - t]--;
}

unsigned long long solve(int hh, int ww, int recur)
{
	int t, cx, cy, x;

	h = hh, w = ww;

	if (h & 1) t = w, w = h, h = t;
	if (h & 1) return 0;
	if (w == 1) return 1;
	if (w == 2) return h;
	if (h == 2) return w;

	cy = h / 2, cx = w / 2;

	len = (h + 1) * (w + 1);
	grid = realloc(grid, len);
	memset(grid, 0, len--);

	next[0] = -1;
	next[1] = -w - 1;
	next[2] = 1;
	next[3] = w + 1;

	if (recur) cnt = 0;
	for (x = cx + 1; x < w; x++) {
		t = cy * (w + 1) + x;
		grid[t] = 1;
		grid[len - t] = 1;
		walk(cy - 1, x);
	}
	cnt++;

	if (h == w)
		cnt *= 2;
	else if (!(w & 1) && recur)
		solve(w, h, 0);

	return cnt;
}

int main()
{
	int y, x;
	for (y = 1; y <= 10; y++)
		for (x = 1; x <= y; x++)
			if (!(x & 1) || !(y & 1))
				printf("%d x %d: %llu\n", y, x, solve(y, x, 1));

	return 0;
}
