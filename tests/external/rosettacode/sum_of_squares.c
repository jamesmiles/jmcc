// TEST: rosetta_sum_of_squares
// DESCRIPTION: Rosetta Code - Sum of squares (double array arithmetic)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Sum_of_squares#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: 133.000000
// STDOUT: 0.000000
// STDOUT: 0.000000

#include <stdio.h>

double squaredsum(double *l, int e)
{
   int i; double sum = 0.0;
   for(i = 0 ; i < e ; i++) sum += l[i]*l[i];
   return sum;
}

int main()
{
   double list[6] = {3.0, 1.0, 4.0, 1.0, 5.0, 9.0};

   printf("%lf\n", squaredsum(list, 6));
   printf("%lf\n", squaredsum(list, 0));
   /* the same without using a real list as if it were 0-element long */
   printf("%lf\n", squaredsum(NULL, 0));
   return 0;
}
