// TEST: ctest_00178
// DESCRIPTION: c-testsuite test 00178
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 4
// STDOUT: 8
// STDOUT: 4

#include <stdio.h>

int main()
{
   char a;
   int b;
   double c;

   printf("%d\n", sizeof(a));
   printf("%d\n", sizeof(b));
   printf("%d\n", sizeof(c));

   printf("%d\n", sizeof(!a));

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
