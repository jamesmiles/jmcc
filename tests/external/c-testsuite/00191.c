// TEST: ctest_00191
// DESCRIPTION: c-testsuite test 00191
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: it's all good

#include <stdio.h>

int main()
{
   int a;

   for (a = 0; a < 2; a++)
   {
      int b = a;
   }

   printf("it's all good\n");

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
