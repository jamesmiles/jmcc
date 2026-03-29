// TEST: ctest_00192
// DESCRIPTION: c-testsuite test 00192
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 2
// STDOUT: 3
// STDOUT: 4
// STDOUT: 5
// STDOUT: 6
// STDOUT: 7
// STDOUT: 8
// STDOUT: 9
// STDOUT: 10

#include <stdio.h>

int main()
{
   int Count = 0;

   for (;;)
   {
      Count++;
      printf("%d\n", Count);
      if (Count >= 10)
         break;
   }

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
