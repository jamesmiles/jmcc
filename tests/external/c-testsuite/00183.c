// TEST: ctest_00183
// DESCRIPTION: c-testsuite test 00183
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 0
// STDOUT: 1
// STDOUT: 4
// STDOUT: 9
// STDOUT: 16
// STDOUT: 15
// STDOUT: 18
// STDOUT: 21
// STDOUT: 24
// STDOUT: 27

#include <stdio.h>

int main()
{
   int Count;

   for (Count = 0; Count < 10; Count++)
   {
      printf("%d\n", (Count < 5) ? (Count*Count) : (Count * 3));
   }

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
