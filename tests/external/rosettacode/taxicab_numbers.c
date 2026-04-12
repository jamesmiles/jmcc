// TEST: rosetta_taxicab_numbers
// DESCRIPTION: Rosetta Code - Taxicab numbers (typedef'd struct array declaration lvalue bug)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Taxicab_numbers#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:    1:      1729 =   12^3 +    1^3 =   10^3 +    9^3
// STDOUT:    2:      4104 =   15^3 +    9^3 =   16^3 +    2^3
// STDOUT:    3:     13832 =   20^3 +   18^3 =   24^3 +    2^3
// STDOUT:    4:     20683 =   27^3 +   10^3 =   24^3 +   19^3
// STDOUT:    5:     32832 =   30^3 +   18^3 =   32^3 +    4^3
// STDOUT:    6:     39312 =   33^3 +   15^3 =   34^3 +    2^3
// STDOUT:    7:     40033 =   33^3 +   16^3 =   34^3 +    9^3
// STDOUT:    8:     46683 =   30^3 +   27^3 =   36^3 +    3^3
// STDOUT:    9:     64232 =   36^3 +   26^3 =   39^3 +   17^3
// STDOUT:   10:     65728 =   33^3 +   31^3 =   40^3 +   12^3
// STDOUT:   11:    110656 =   40^3 +   36^3 =   48^3 +    4^3
// STDOUT:   12:    110808 =   45^3 +   27^3 =   48^3 +    6^3
// STDOUT:   13:    134379 =   43^3 +   38^3 =   51^3 +   12^3
// STDOUT:   14:    149389 =   50^3 +   29^3 =   53^3 +    8^3
// STDOUT:   15:    165464 =   48^3 +   38^3 =   54^3 +   20^3
// STDOUT:   16:    171288 =   54^3 +   24^3 =   55^3 +   17^3
// STDOUT:   17:    195841 =   57^3 +   22^3 =   58^3 +    9^3
// STDOUT:   18:    216027 =   59^3 +   22^3 =   60^3 +    3^3
// STDOUT:   19:    216125 =   50^3 +   45^3 =   60^3 +    5^3
// STDOUT:   20:    262656 =   60^3 +   36^3 =   64^3 +    8^3
// STDOUT:   21:    314496 =   66^3 +   30^3 =   68^3 +    4^3
// STDOUT:   22:    320264 =   66^3 +   32^3 =   68^3 +   18^3
// STDOUT:   23:    327763 =   58^3 +   51^3 =   67^3 +   30^3
// STDOUT:   24:    373464 =   60^3 +   54^3 =   72^3 +    6^3
// STDOUT:   25:    402597 =   61^3 +   56^3 =   69^3 +   42^3
// STDOUT: 2000:1671816384 = 1168^3 +  428^3 =  944^3 +  940^3
// STDOUT: 2001:1672470592 = 1124^3 +  632^3 = 1187^3 +   29^3
// STDOUT: 2002:1673170856 = 1034^3 +  828^3 = 1164^3 +  458^3
// STDOUT: 2003:1675045225 = 1153^3 +  522^3 = 1081^3 +  744^3
// STDOUT: 2004:1675958167 = 1096^3 +  711^3 = 1159^3 +  492^3
// STDOUT: 2005:1676926719 = 1188^3 +   63^3 = 1095^3 +  714^3
// STDOUT: 2006:1677646971 =  990^3 +  891^3 = 1188^3 +   99^3

#include <stdio.h>
#include <stdlib.h>

typedef unsigned long long xint;
typedef unsigned uint;
typedef struct {
	uint x, y; // x > y always
	xint value;
} sum_t;

xint *cube;
uint n_cubes;

sum_t *pq;
uint pq_len, pq_cap;

void add_cube(void)
{
	uint x = n_cubes++;
	cube = realloc(cube, sizeof(xint) * (n_cubes + 1));
	cube[n_cubes] = (xint) n_cubes*n_cubes*n_cubes;
	if (x < 2) return; // x = 0 or 1 is useless

	if (++pq_len >= pq_cap) {
		if (!(pq_cap *= 2)) pq_cap = 2;
		pq = realloc(pq, sizeof(*pq) * pq_cap);
	}

	sum_t tmp = (sum_t) { x, 1, cube[x] + 1 };
	// upheap
	uint i, j;
	for (i = pq_len; i >= 1 && pq[j = i>>1].value > tmp.value; i = j)
		pq[i] = pq[j];

	pq[i] = tmp;
}

void next_sum(void)
{
redo:	while (!pq_len || pq[1].value >= cube[n_cubes]) add_cube();

	sum_t tmp = pq[0] = pq[1];	// pq[0] always stores last seen value
	if (++tmp.y >= tmp.x) {		// done with this x; throw it away
		tmp = pq[pq_len--];
		if (!pq_len) goto redo;	// refill empty heap
	} else
		tmp.value += cube[tmp.y] - cube[tmp.y-1];

	uint i, j;
	// downheap
	for (i = 1; (j = i<<1) <= pq_len; pq[i] = pq[j], i = j) {
		if (j < pq_len && pq[j+1].value < pq[j].value) ++j;
		if (pq[j].value >= tmp.value) break;
	}
	pq[i] = tmp;
}

uint next_taxi(sum_t *hist)
{
	do next_sum(); while (pq[0].value != pq[1].value);

	uint len = 1;
	hist[0] = pq[0];
	do {
		hist[len++] = pq[1]; 
		next_sum();
	} while (pq[0].value == pq[1].value);

	return len;
}

int main(void)
{
	uint i, l;
	sum_t x[10];
	for (i = 1; i <= 2006; i++) {
		l = next_taxi(x);
		if (25 < i && i < 2000) continue;
		printf("%4u:%10llu", i, x[0].value);
		while (l--) printf(" = %4u^3 + %4u^3", x[l].x, x[l].y);
		putchar('\n');
	}
	return 0;
}
