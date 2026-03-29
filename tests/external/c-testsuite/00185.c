// TEST: ctest_00185
// DESCRIPTION: c-testsuite test 00185
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 0: 12
// STDOUT: 1: 34
// STDOUT: 2: 56
// STDOUT: 3: 78
// STDOUT: 4: 90
// STDOUT: 5: 123
// STDOUT: 6: 456
// STDOUT: 7: 789
// STDOUT: 8: 8642
// STDOUT: 9: 9753
// STDOUT: 0: 12
// STDOUT: 1: 34
// STDOUT: 2: 56
// STDOUT: 3: 78
// STDOUT: 4: 90
// STDOUT: 5: 123
// STDOUT: 6: 456
// STDOUT: 7: 789
// STDOUT: 8: 8642
// STDOUT: 9: 9753

#include <stdio.h>

int main()
{
   int Count;

   int Array[10] = { 12, 34, 56, 78, 90, 123, 456, 789, 8642, 9753 };

   for (Count = 0; Count < 10; Count++)
      printf("%d: %d\n", Count, Array[Count]);

   int Array2[10] = { 12, 34, 56, 78, 90, 123, 456, 789, 8642, 9753, };

   for (Count = 0; Count < 10; Count++)
      printf("%d: %d\n", Count, Array2[Count]);


   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
