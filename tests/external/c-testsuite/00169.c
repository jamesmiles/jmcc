// TEST: ctest_00169
// DESCRIPTION: c-testsuite test 00169
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 0 0 0
// STDOUT: 0 0 1
// STDOUT: 0 0 2
// STDOUT: 0 1 0
// STDOUT: 0 1 1
// STDOUT: 0 1 2
// STDOUT: 0 2 0
// STDOUT: 0 2 1
// STDOUT: 0 2 2
// STDOUT: 1 0 0
// STDOUT: 1 0 1
// STDOUT: 1 0 2
// STDOUT: 1 1 0
// STDOUT: 1 1 1
// STDOUT: 1 1 2
// STDOUT: 1 2 0
// STDOUT: 1 2 1
// STDOUT: 1 2 2

#include <stdio.h>

int main()
{
   int x, y, z;

   for (x = 0; x < 2; x++)
   {
      for (y = 0; y < 3; y++)
      {
         for (z = 0; z < 3; z++)
         {
            printf("%d %d %d\n", x, y, z);
         }
      }
   }

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
