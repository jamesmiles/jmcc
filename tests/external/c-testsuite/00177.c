// TEST: ctest_00177
// DESCRIPTION: c-testsuite test 00177
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: 1
// STDOUT: 8
// STDOUT: 64
// STDOUT: 1
// STDOUT: 14
// STDOUT: 16
// STDOUT: 64
// STDOUT: test @

#include <stdio.h>

int main()
{
   printf("%d\n", '\1');
   printf("%d\n", '\10');
   printf("%d\n", '\100');
   printf("%d\n", '\x01');
   printf("%d\n", '\x0e');
   printf("%d\n", '\x10');
   printf("%d\n", '\x40');
   printf("test \x40\n");

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
