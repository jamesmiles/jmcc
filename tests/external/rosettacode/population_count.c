// TEST: rosetta_population_count
// DESCRIPTION: Rosetta Code - Population count (link)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Population_count#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 1 2 2 4 3 6 6 5 6 8 9 13 10 11 14 15 11 14 14 17 17 20 19 22 16 18 24 30 25 25 
// STDOUT: evil  : 0 3 5 6 9 10 12 15 17 18 20 23 24 27 29 30 33 34 36 39 40 43 45 46 48 51 53 54 57 58 
// STDOUT: odious: 1 2 4 7 8 11 13 14 16 19 21 22 25 26 28 31 32 35 37 38 41 42 44 47 49 50 52 55 56 59 

#include <stdio.h>

int main() {
  {
    unsigned long long n = 1;
    for (int i = 0; i < 30; i++) {
      // __builtin_popcount() for unsigned int
      // __builtin_popcountl() for unsigned long
      // __builtin_popcountll() for unsigned long long
      printf("%d ", __builtin_popcountll(n));
      n *= 3;
    }
    printf("\n");
  }

  int od[30];
  int ne = 0, no = 0;
  printf("evil  : ");
  for (int n = 0; ne+no < 60; n++) {
    if ((__builtin_popcount(n) & 1) == 0) {
      if (ne < 30) {
	printf("%d ", n);
	ne++;
      }
    } else {
      if (no < 30) {
	od[no++] = n;
      }
    }
  }
  printf("\n");
  printf("odious: ");
  for (int i = 0; i < 30; i++) {
    printf("%d ", od[i]);
  }
  printf("\n");

  return 0;
}