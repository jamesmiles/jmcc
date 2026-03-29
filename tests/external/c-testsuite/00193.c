// TEST: ctest_00193
// DESCRIPTION: c-testsuite test 00193
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 2
// STDOUT: out
// STDOUT: 3

#include <stdio.h>

void fred(int x)
{
   switch (x)
   {
      case 1: printf("1\n"); return;
      case 2: printf("2\n"); break;
      case 3: printf("3\n"); return;
   }

   printf("out\n");
}

int main()
{
   fred(1);
   fred(2);
   fred(3);

   return 0;
}    

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
