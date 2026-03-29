// TEST: ctest_00156
// DESCRIPTION: c-testsuite test 00156
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
   int Count;

   for (Count = 1; Count <= 10; Count++)
   {
      printf("%d\n", Count);
   }

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
