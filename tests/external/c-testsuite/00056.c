// TEST: ctest_00056
// DESCRIPTION: c-testsuite test 00056
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 42
// STDOUT: 64
// STDOUT: 12, 34

#include <stdio.h>

int main() 
{
   int a;
   a = 42;
   printf("%d\n", a);

   int b = 64;
   printf("%d\n", b);

   int c = 12, d = 34;
   printf("%d, %d\n", c, d);

   return 0;
}

// vim: set expandtab ts=4 sw=3 sts=3 tw=80 :
