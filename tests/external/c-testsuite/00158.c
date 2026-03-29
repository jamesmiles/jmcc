// TEST: ctest_00158
// DESCRIPTION: c-testsuite test 00158
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 0
// STDOUT: 0
// STDOUT: 1
// STDOUT: 1
// STDOUT: 2
// STDOUT: 2
// STDOUT: 3
// STDOUT: 0

#include <stdio.h>

int main()
{
   int Count;

   for (Count = 0; Count < 4; Count++)
   {
      printf("%d\n", Count);
      switch (Count)
      {
         case 1:
            printf("%d\n", 1);
            break;

         case 2:
            printf("%d\n", 2);
            break;

         default:
            printf("%d\n", 0);
            break;
      }
   }

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
