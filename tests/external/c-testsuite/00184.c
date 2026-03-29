// TEST: ctest_00184
// DESCRIPTION: c-testsuite test 00184
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1 1
// STDOUT: 2 2

#include <stdio.h>

int main()
{
   char a;
   short b;

   printf("%d %d\n", sizeof(char), sizeof(a));
   printf("%d %d\n", sizeof(short), sizeof(b));

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
