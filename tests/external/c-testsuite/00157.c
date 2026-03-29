// TEST: ctest_00157
// DESCRIPTION: c-testsuite test 00157
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 4
// STDOUT: 9
// STDOUT: 16
// STDOUT: 25
// STDOUT: 36
// STDOUT: 49
// STDOUT: 64
// STDOUT: 81
// STDOUT: 100

#include <stdio.h>

int main() 
{
   int Count;
   int Array[10];

   for (Count = 1; Count <= 10; Count++)
   {
      Array[Count-1] = Count * Count;
   }

   for (Count = 0; Count < 10; Count++)
   {
      printf("%d\n", Array[Count]);
   }

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
