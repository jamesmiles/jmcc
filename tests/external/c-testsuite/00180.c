// TEST: ctest_00180
// DESCRIPTION: c-testsuite test 00180
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4
// STDOUT: bcdef

#include <stdio.h>
#include <string.h>

int main()
{
   char a[10];
   strcpy(a, "abcdef");
   printf("%s\n", &a[1]);

   return 0;
}

/* vim: set expandtab ts=4 sw=3 sts=3 tw=80 :*/
