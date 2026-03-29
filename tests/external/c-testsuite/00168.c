// TEST: ctest_00168
// DESCRIPTION: c-testsuite test 00168
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 2
// STDOUT: 6
// STDOUT: 24
// STDOUT: 120
// STDOUT: 720
// STDOUT: 5040
// STDOUT: 40320
// STDOUT: 362880
// STDOUT: 3628800

#include <stdio.h>

int factorial(int i) 
{
   if (i < 2)
      return i;
   else
      return i * factorial(i - 1);
}

int main()
{
   int Count;

   for (Count = 1; Count <= 10; Count++)
      printf("%d\n", factorial(Count));

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
